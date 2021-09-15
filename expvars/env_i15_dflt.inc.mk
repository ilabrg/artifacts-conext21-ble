# Configure connection manager params
CFLAGS += -DNIMBLE_RPBLE_CONN_ITVL_MIN=15000
CFLAGS += -DNIMBLE_RPBLE_CONN_ITVL_MAX=15000
CFLAGS += -DNIMBLE_RPBLE_CONN_LATENCY=0
CFLAGS += -DNIMBLE_RPBLE_CONN_SUPER_TO=1500000

CFLAGS += -DNIMBLE_AUTOCONN_CONN_ITVL_MS=15
CFLAGS += -DNIMBLE_AUTOCONN_CONN_LATENCY=0
CFLAGS += -DNIMBLE_AUTOCONN_CONN_SVTO_MS=1500

CFLAGS += -DNIMBLE_STATCONN_CONN_ITVL_MS=15
CFLAGS += -DNIMBLE_STATCONN_CONN_LATENCY=0
CFLAGS += -DNIMBLE_STATCONN_CONN_SUPERTO_MS=1500