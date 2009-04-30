/* Describes message structure used for communication
 */

#ifndef MESSAGE_H
#define MESSAGE_H

enum geni_call {
	LIST_COMPONENTS,
	START_SLICE,
    STOP_SLICE
};

struct CH_msg
{
	/* GENI call */
	geni_call func;

	char slice_name[20];
	char rspec[1000];
};

#endif
