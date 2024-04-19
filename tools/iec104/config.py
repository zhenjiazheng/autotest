# import argparse
from .asdu_type import *

line_separator = '\n'

# parser = argparse.ArgumentParser()
# parser.add_argument('--head', action='store_true', help='Print only APCI part of telegram')
# parser.add_argument('--body', action='store_true', help='Print only ASDU part of telegram')
# parser.add_argument('--less', action='store_true', help='Print result more compact')
# args = parser.parse_args()

HEAD = False
BODY = False
LESS = False

if LESS:
    line_separator = ', '

# %% 104 configuration dictionary
ASDU_TYPE = {
    # 'ASDU type in HEX': {'dec': ASDU type in dec,
    #                     'referece': 'referece type name',
    #                     'format': [list of element in ASDU type],
    #                     'valid_COT': [list of valid COT for ASDU type],
    #                     'func': function name from asdu_type.py}

    # Process information in monitor direction
    '01': {'dec': 1, 'reference': 'M_SP_NA_1', 'format': ['SIQ'],
           'valid_COT': [2, 3, 5, 11, 20], 'func': type_1},
    '02': {'dec': 2, 'reference': 'M_SP_TA_1', 'format': ['SIQ', 'CP24Time2a'],
           'valid_COT': [3, 5, 11, 12], 'func': type_2},
    '03': {'dec': 3, 'reference': 'M_DP_NA_1', 'format': ['DIQ'],
           'valid_COT': [2, 3, 5, 11, 20], 'func': type_3},
    '04': {'dec': 4, 'reference': 'M_DP_TA_1', 'format': ['DIQ', 'CP24Time2a'],
           'valid_COT': [3, 5, 11, 12], 'func': type_4},
    '05': {'dec': 5, 'reference': 'M_ST_NA_1', 'format': ['VTI', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 20], 'func': type_5},
    '06': {'dec': 6, 'reference': 'M_ST_TA_1', 'format': ['VTI', 'QDS', 'CP24Time2a'],
           'valid_COT': [2, 3, 5, 11, 12], 'func': type_6},
    '07': {'dec': 7, 'reference': 'M_BO_NA_1', 'format': ['BSI', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_7},
    '08': {'dec': 8, 'reference': 'M_BO_TA_1', 'format': ['BSI', 'QDS', 'CP24Time2a'],
           'valid_COT': [3, 5], 'func': type_8},
    '09': {'dec': 9, 'reference': 'M_ME_NA_1', 'format': ['NVA', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_9},
    '0A': {'dec': 10, 'reference': 'M_ME_TA_1', 'format': ['NVA', 'QDS', 'CP24Time2a'],
           'valid_COT': [3, 5], 'func': type_a},
    '0B': {'dec': 11, 'reference': 'M_ME_NB_1', 'format': ['SVA', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_b},
    '0C': {'dec': 12, 'reference': 'M_ME_TB_1', 'format': ['SVA', 'QDS', 'CP24Time2a'],
           'valid_COT': [3, 5], 'func': type_c},
    '0D': {'dec': 13, 'reference': 'M_ME_NC_1', 'format': ['IEEE_STD_754', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_d},
    '0E': {'dec': 14, 'reference': 'M_ME_TC_1', 'format': ['IEEE_STD_754', 'QDS', 'CP24Time2a'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_e},
    '0F': {'dec': 15, 'reference': 'M_IT_NA_1', 'format': ['BCR'],
           'valid_COT': [2, 37], 'func': type_in_development},
    '10': {'dec': 16, 'reference': 'M_IT_TA_1', 'format': ['BCR', 'CP24Time2a'],
           'valid_COT': [3, 37], 'func': type_in_development},
    '11': {'dec': 17, 'reference': 'M_EP_TA_1', 'format': ['CP16Time2a', 'CP24Time2a'],
           'valid_COT': [3], 'func': type_in_development},
    '12': {'dec': 18, 'reference': 'M_EP_TB_1', 'format': ['SEP', 'QDP', 'CP16Time2a', 'CP24Time2a'],
           'valid_COT': [3], 'func': type_in_development},
    '13': {'dec': 19, 'reference': 'M_EP_TC_1', 'format': ['OCI', 'QDP', 'CP16Time2a', 'CP24Time2a'],
           'valid_COT': [3], 'func': type_in_development},
    '14': {'dec': 20, 'reference': 'M_PS_NA_1', 'format': ['SCD', 'QDS'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_in_development},
    '15': {'dec': 21, 'reference': 'M_ME_ND_1', 'format': ['NVA'],
           'valid_COT': [1, 2, 3, 5, 11, 12, 20], 'func': type_15},
    # Process telegrams with long time tag (7 octets )
    '1E': {'dec': 30, 'reference': 'M_SP_TB_1', 'format': ['SIQ', 'CP56Time2a'],
           'valid_COT': [3, 5, 11, 12], 'func': type_1e},
    '1F': {'dec': 31, 'reference': 'M_DP_TB_1', 'format': ['DIQ', 'CP56Time2a'],
           'valid_COT': [3, 5, 11, 12], 'func': type_1f},
    '20': {'dec': 32, 'reference': 'M_ST_TB_1', 'format': ['VTI', 'QDS', 'CP56Time2a'],
           'valid_COT': [2, 3, 5, 11, 12], 'func': type_20},
    '21': {'dec': 33, 'reference': 'M_BO_TB_1', 'format': ['BSI', 'QDS', 'CP56Time2a'],
           'valid_COT': [3, 5], 'func': type_21},
    '22': {'dec': 34, 'reference': 'M_ME_TD_1', 'format': ['NVA', 'QDS', 'CP56Time2a'],
           'valid_COT': [3, 5], 'func': type_22},
    '23': {'dec': 35, 'reference': 'M_ME_TE_1', 'format': ['SVA', 'QDS', 'CP56Time2a'],
           'valid_COT': [3, 5], 'func': type_23},
    '24': {'dec': 36, 'reference': 'M_ME_TF_1', 'format': ['IEEE_STD_754', 'QDS', 'CP56Time2a'],
           'valid_COT': [2, 3, 5, 11, 12, 20], 'func': type_24},
    '25': {'dec': 37, 'reference': 'M_IT_TB_1', 'format': ['BCR', 'CP56Time2a'],
           'valid_COT': [3, 37], 'func': type_in_development},
    '26': {'dec': 38, 'reference': 'M_EP_TD_1', 'format': ['CP16Time2a', 'CP56Time2a'],
           'valid_COT': [3], 'func': type_26},
    '27': {'dec': 39, 'reference': 'M_EP_TE_1', 'format': ['SEP', 'QDP', 'CP56Time2a'],
           'valid_COT': [3], 'func': type_in_development},
    '28': {'dec': 40, 'reference': 'M_EP_TF_1', 'format': ['OCI', 'QDP', 'CP16Time2a', 'CP56Time2a'],
           'valid_COT': [3], 'func': type_in_development},
    # Process information in control direction
    '2D': {'dec': 45, 'reference': 'C_SC_NA_1', 'format': ['IOA', 'SCO'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '2E': {'dec': 46, 'reference': 'C_DC_NA_1', 'format': ['IOA', 'DCO'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '2F': {'dec': 47, 'reference': 'C_RC_NA_1', 'format': ['IOA', 'RCO'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '30': {'dec': 48, 'reference': 'C_SE_NA_1', 'format': ['IOA', 'NVA', 'QOS'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '31': {'dec': 49, 'reference': 'C_SE_NB_1', 'format': ['IOA', 'SVA', 'QOS'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '32': {'dec': 50, 'reference': 'C_SE_NC_1', 'format': ['IOA', 'IEEE_STD_754', 'QOS'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    '33': {'dec': 51, 'reference': 'C_BO_NA_1', 'format': ['IOA', 'BSI'],
           'valid_COT': [6, 7, 8, 9, 10, 44, 45, 46, 47], 'func': type_in_development},
    # Command telegrams with long time tag
    '3A': {'dec': 58, 'reference': 'C_SC_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '3B': {'dec': 59, 'reference': 'C_DC_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '3C': {'dec': 60, 'reference': 'C_RC_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '3D': {'dec': 61, 'reference': 'C_SE_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '3E': {'dec': 62, 'reference': 'C_SE_TB_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '3F': {'dec': 63, 'reference': 'C_SE_TC_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '40': {'dec': 64, 'reference': 'C_BO_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    # System information in monitor direction
    '46': {'dec': 70, 'reference': 'M_EI_NA_1', 'format': ['COI'],
           'valid_COT': [4], 'func': type_in_development},
    # System information in control direction
    '64': {'dec': 100, 'reference': 'C_IC_NA_1', 'format': ['QOI'],
           'valid_COT': [], 'func': type_64},
    '65': {'dec': 101, 'reference': 'C_CI_NA_1', 'format': ['QCC'],
           'valid_COT': [], 'func': type_in_development},
    '66': {'dec': 102, 'reference': 'C_RD_NA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    '67': {'dec': 103, 'reference': 'C_CS_NA_1', 'format': ['CP56Time2a'],
           'valid_COT': [], 'func': type_in_development},
    '68': {'dec': 104, 'reference': 'C_TS_NB_1', 'format': ['FBP'],
           'valid_COT': [], 'func': type_in_development},
    '69': {'dec': 105, 'reference': 'C_RP_NC_1', 'format': ['QRP'],
           'valid_COT': [], 'func': type_in_development},
    '6A': {'dec': 106, 'reference': 'C_CD_NA_1', 'format': ['CP16Time2a'],
           'valid_COT': [], 'func': type_in_development},
    '6B': {'dec': 107, 'reference': 'C_TS_TA_1', 'format': [''],
           'valid_COT': [], 'func': type_in_development},
    # Parameter in control direction
    '6E': {'dec': 110, 'reference': 'P_ME_NA_1', 'format': ['NVA', 'QPM'],
           'valid_COT': [], 'func': type_in_development},
    '6F': {'dec': 111, 'reference': 'P_ME_NB_1', 'format': ['SVA', 'QPM'],
           'valid_COT': [], 'func': type_in_development},
    '70': {'dec': 112, 'reference': 'P_ME_NC_1', 'format': ['IEEE_STD_754', 'QPM'],
           'valid_COT': [], 'func': type_in_development},
    '71': {'dec': 113, 'reference': 'P_AC_NA_1', 'format': ['QPA'],
           'valid_COT': [], 'func': type_in_development},
    # File transfer
    '78': {'dec': 120, 'reference': 'F_FR_NA_1', 'format': ['NOF', 'LOF', 'FRQ'],
           'valid_COT': [], 'func': type_in_development},
    '79': {'dec': 121, 'reference': 'F_SR_NA_1', 'format': ['NOF', 'NOS', 'LOF', 'SRQ'],
           'valid_COT': [], 'func': type_in_development},
    '7A': {'dec': 122, 'reference': 'F_SC_NA_1', 'format': ['NOF', 'NOS', 'SCQ'],
           'valid_COT': [], 'func': type_in_development},
    '7B': {'dec': 123, 'reference': 'F_LS_NA_1', 'format': ['NOF', 'NOS', 'LSQ', 'CHS'],
           'valid_COT': [], 'func': type_in_development},
    '7C': {'dec': 124, 'reference': 'F_AF_NA_1', 'format': ['NOF', 'NOS', 'AFQ'],
           'valid_COT': [], 'func': type_in_development},
    '7D': {'dec': 125, 'reference': 'F_SG_NA_1', 'format': ['NOF', 'NOS', 'LOS', 'segment'],
           'valid_COT': [], 'func': type_in_development},
    '7E': {'dec': 126, 'reference': 'F_DR_TA_1', 'format': ['NOF', 'LOF', 'SOF', 'CP56Time2a'],
           'valid_COT': [], 'func': type_in_development},
    '7F': {'dec': 127, 'reference': 'F_SC_NB_1', 'format': [],
           'valid_COT': [], 'func': type_in_development}
}

information_elements_length = {
    # Process information in monitor direction
    'SIQ': 1, 'DIQ': 1, 'BSI': 4, 'SCD': 4, 'QDS': 1, 'VTI': 1,
    'NVA': 2, 'SVA': 2, 'IEEE_STD_754': 4, 'BCR': 5,
    # Protection
    'SEP': 1, 'SPE': 1, 'OCI': 1, 'QDP': 1,
    # Commands
    'SCO': 1, 'DCO': 1, 'RCO': 1,
    # Time
    'CP56Time2a': 7, 'CP24Time2a': 3, 'CP16Time2a': 2,
    # Qualifiers
    'QOI': 1, 'QCC': 1, 'QPM': 1, 'QPA': 1, 'QRP': 1, 'QOC': 1, 'QOS': 1,
    # File Transfer
    'FRQ': 1, 'SRQ': 1, 'SCQ': 1, 'LSQ': 1, 'AFQ': 1, 'NOF': 2, 'NOS': 2, 'LOF': 3, 'LOS': 1, 'CHS': 1, 'SOF': 1,
    'COI': 1, 'FBP': 2
}

cot_dict = {0: 'Not used', 1: 'Cyclic data', 2: 'Background request', 3: 'Spontaneous data',
            4: 'End of initialisation', 5: 'Read-Request', 6: 'Command activation',
            7: 'Acknowledgement of command activation', 8: 'Command abort',
            9: 'Acknowledgement of command abort', 10: 'Termination of command activation',
            11: 'Return because of remote command', 12: 'Return because local command',
            13: 'File access',
            20: 'Station interrogation (general)',
            **{i: f'Station interrogation of group {i - 20}' for i in range(21, 37)},
            37: 'Counter request (general)', 38: 'Counter request of group 1',
            39: 'Counter request of group 2', 40: 'Counter request of group 3',
            41: 'Counter request of group 4',
            44: 'Unknown type', 45: 'Unknown transmission cause', 46: 'Unknown collective ASDU address',
            47: 'Unknown object address'}

u_type_dict = {'43': 'Test Frame Activation',
               '83': 'Test Frame Confirmation',
               '13': 'Stop Data Transfer Activation',
               '23': 'Stop Data Transfer Confirmation',
               '07': 'Start Data Transfer Activation',
               '0B': 'Start Data Transfer Confirmation'}
