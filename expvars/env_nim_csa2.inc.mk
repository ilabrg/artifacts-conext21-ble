# Configure NimBLE
CFLAGS += -DMYNEWT_VAL_BLE_LL_TX_PWR_DBM=0 # -> default, but lets set it here explicitly

# No need to do this... So we go with the default configuration
#CFLAGS += -DMYNEWT_VAL_BLE_LL_MAX_PKT_SIZE=251 -> this is default
#CFLAGS += -DMYNEWT_VAL_BLE_L2CAP_COC_MPS=200
#CFLAGS += -DMYNEWT_VAL_BLE_LL_CFG_FEAT_DATA_LEN_EXT=1 -> default by nimble_netif

# Limit slot size to 1.25ms to reduce chance of slaves massively skipping
# conn events
# CFLAGS += -DMYNEWT_VAL_BLE_LL_CONN_INIT_SLOTS=1

# try strict scheduling: has it any influence on our setups?
# CFLAGS += -DMYNEWT_VAL_BLE_LL_STRICT_CONN_SCHEDULING=1
# CFLAGS += -DMYNEWT_VAL_BLE_LL_ADD_STRICT_SCHED_PERIODS=2
#
#


CFLAGS += -DMYNEWT_VAL_BLE_LL_CFG_FEAT_LE_CSA2=1
