/*
 * Copyright (C) 2020 Freie Universität Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     exp_coap_m3
 * @{
 *
 * @file
 * @brief       exp CoAP-NON M3
 *
 * @author      Hauke Petersen <hauke.petersen@fu-berlin.de>
 *
 * @}
 */

#include "myprint.h"
#include "alive.h"
#include "coapexp.h"

int main(void)
{
    myputs(APPNAME);

    alive_run();
    coapexp_run();

    return 0;
}
