# from django.dispatch import receiver
# from bomiot.server.core.signal import bomiot_signals
#
# @receiver(bomiot_signals)
# def bomiot_signal_callback(sender, **kwargs):
#     print(kwargs['msg'])


bar_code = {
    'bin_name': 'A00001',
    't_code': '11111111111111',
    '2024-11-11': {
        'from_bin': 'A00002',
        'to_bin': 'A00001'
    },
}