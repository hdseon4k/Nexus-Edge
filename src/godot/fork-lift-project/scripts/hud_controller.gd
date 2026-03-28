# scripts/hud_controller.gd
extends CanvasLayer

@onready var speed_label = $MarginContainer/VBoxContainer/SpeedLabel
@onready var status_label = $MarginContainer/VBoxContainer/StatusLabel


func update_speed(speed_mps):
	# 속도를 m/s 단위로 받아와 소수점 한 자리까지 표시
	speed_label.text = "Speed: %.1f m/s" % speed_mps


func update_status(new_status):
	# 지게차의 현재 상태(예: "주행 중", "정지", "장애물 감지")를 표시
	status_label.text = "Status: %s" % new_status
