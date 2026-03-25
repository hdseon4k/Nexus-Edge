#include "POUS.h"
#include "Config0.h"

void MAIN_init__(MAIN *data__, BOOL retain) {
  TON_init__(&data__->T1,retain);
  __INIT_VAR(data__->BLINK_STATE,__BOOL_LITERAL(FALSE),retain)
  __INIT_LOCATED(BOOL,__IX0_0,data__->PB1,retain)
  __INIT_LOCATED_VALUE(data__->PB1,__BOOL_LITERAL(FALSE))
  __INIT_LOCATED(BOOL,__QX0_1,data__->LED,retain)
  __INIT_LOCATED_VALUE(data__->LED,__BOOL_LITERAL(FALSE))
}

// Code part
void MAIN_body__(MAIN *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->T1.,IN,,!(__GET_VAR(data__->T1.Q,)));
  __SET_VAR(data__->T1.,PT,,__time_to_timespec(1, 0, 1, 0, 0, 0));
  TON_body__(&data__->T1);
  if (__GET_VAR(data__->T1.Q,)) {
    __SET_VAR(data__->,BLINK_STATE,,!(__GET_VAR(data__->BLINK_STATE,)));
  };
  __SET_LOCATED(data__->,LED,,__GET_VAR(data__->BLINK_STATE,));

  goto __end;

__end:
  return;
} // MAIN_body__() 





