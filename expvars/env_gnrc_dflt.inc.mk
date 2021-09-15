# Configure GNRC
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_OFFL_NUMOF=32
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_NUMOF=16
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_NO_RTR_SOL=1


# default: 4
CFLAGS += -DCONFIG_GNRC_NETIF_MSG_QUEUE_SIZE_EXP=5
# default 3
CFLAGS += -DCONFIG_GNRC_IPV6_MSG_QUEUE_SIZE_EXP=5
CFLAGS += -DCONFIG_GNRC_SIXLOWPAN_MSG_QUEUE_SIZE_EXP=5
CFLAGS += -DCONFIG_GNRC_UDP_MSG_QUEUE_SIZE_EXP=5
CFLAGS += -DCONFIG_GNRC_SOCK_MBOX_SIZE_EXP=5