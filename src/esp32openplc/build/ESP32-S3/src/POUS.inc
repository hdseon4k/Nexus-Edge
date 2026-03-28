#include "POUS.h"
#include "Config0.h"

void MAIN_init__(MAIN *data__, BOOL retain) {
  TON_init__(&data__->BLINKTIMER,retain);
  __INIT_VAR(data__->LED_STATE,__BOOL_LITERAL(FALSE),retain)
  __INIT_LOCATED(BOOL,__QX0_0,data__->WS2812_OUT,retain)
  __INIT_LOCATED_VALUE(data__->WS2812_OUT,__BOOL_LITERAL(FALSE))
}

// Code part
void MAIN_body__(MAIN *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->BLINKTIMER.,IN,,!(__GET_VAR(data__->BLINKTIMER.Q,)));
  __SET_VAR(data__->BLINKTIMER.,PT,,__time_to_timespec(1, 0, 1, 0, 0, 0));
  TON_body__(&data__->BLINKTIMER);
  if (__GET_VAR(data__->BLINKTIMER.Q,)) {
    __SET_VAR(data__->,LED_STATE,,!(__GET_VAR(data__->LED_STATE,)));
  };
  __SET_LOCATED(data__->,WS2812_OUT,,__GET_VAR(data__->LED_STATE,));

  goto __end;

__end:
  return;
} // MAIN_body__() 





