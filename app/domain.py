from collections import defaultdict
from statistics import mean, stdev


def reading_groups(data):
    instruments = {row['id']: row for row in data['instruments']}
    groups = defaultdict(list)
    identities = set()
    for row in data['readings']:
        identity = (row['specimen'], row['operator'], row['instrument'], row['replicate'])
        if identity in identities:
            raise ValueError('重复读数编号')
        identities.add(identity)
        instrument = instruments[row['instrument']]
        if row['unit'] != instrument['unit']:
            raise ValueError('读数单位与设备不一致')
        if not instrument['minimum'] <= row['value'] <= instrument['maximum']:
            raise ValueError('读数超出量程')
        groups[identity[:3]].append(row['value'])
    return groups


def baseline(data):
    groups = reading_groups(data)
    return {'groups': len(groups), 'readings': sum(map(len, groups.values())),
            'repeat_groups': sum(len(values) > 1 for values in groups.values()),
            'design': data['study_design'], 'notice': '总散布不等于测量误差'}


def act(data, request):
    if request.get('operation') != 'repeatability':
        raise ValueError('未知精度簿操作')
    instrument = request['instrument']
    if instrument not in {row['id'] for row in data['instruments']}:
        raise ValueError('未登记设备')
    summaries = []
    for key, values in sorted(reading_groups(data).items()):
        if key[2] != instrument:
            continue
        summaries.append({'specimen': key[0], 'operator': key[1], 'n': len(values),
                          'mean': mean(values), 'range': max(values) - min(values),
                          'standard_deviation': stdev(values) if len(values) > 1 else None})
    return {'instrument': instrument, 'repeatability': summaries,
            'notice': '同一组合内描述，不外推人员或设备分量'}
