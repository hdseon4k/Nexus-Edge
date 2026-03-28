PROGRAM main
VAR
	ColorTimer : TON;
	LED_State : int := 0;
	LED_Color : dword;
END_VAR

(* 1. 1초 타이머 설정: ColorTimer.Q가 False일 때 작동 시작, 1초 후 True 반환 *)
ColorTimer(IN := NOT ColorTimer.Q, PT := T#1s);

(* 2. 타이머가 완료(1초 경과)될 때마다 실행 *)
IF ColorTimer.Q THEN
    (* 내부 상태 값을 반전 (False -> True -> False) *)
    LED_State := NOT LED_State;
END_IF;

(* 3. 실제 아두이노 13번 핀(%QX0.6)으로 신호 전송 *)
LED_Color := LED_State;

END_PROGRAM