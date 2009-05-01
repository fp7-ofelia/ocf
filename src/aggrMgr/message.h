/* Describes message structure used for communication
 */

#ifndef MESSAGE_H
#define MESSAGE_H

enum geni_call {
    SFA_START_SLICE = 101,
    SFA_STOP_SLICE = 102,
    SFA_CREATE_SLICE = 103,
    SFA_DELETE_SLICE = 104,
    SFA_LIST_SLICES = 105,
    SFA_LIST_COMPONENTS = 106,
    SFA_REGISTER = 107,
    SFA_REBOOT_COMPONENT = 108,
};

#endif
