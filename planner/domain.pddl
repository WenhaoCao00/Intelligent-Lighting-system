(define
	(domain smartbloomsystem)
	(:requirements :strips :typing)
	(:types
		light
		lighttime
		moisture
		temp
	)
	(:predicates
		(lightTime-is-enough ?lt - lighttime)
		(light-is-off ?l - light)
		(light-is-on ?l - light)
		(moisture-is-high ?m - moisture)
		(moisture-is-low ?m - moisture)
		(moisture-is-ok ?m - moisture)
		(temp-is-high ?t - temp)
		(temp-is-low ?t - temp)
		(temp-is-ok ?t - temp)
	)
	(:action light-keep-off-1
		:parameters (?l - light ?t - temp)
		:precondition (and (light-is-off ?l) (temp-is-high ?t))
		:effect (and (not (temp-is-high ?t)) (temp-is-ok ?t))
	)
	(:action light-keep-off-2
		:parameters (?l - light ?t - temp)
		:precondition (and (light-is-off ?l) (temp-is-ok ?t))
		:effect (and (not (temp-is-ok ?t)) (temp-is-low ?t))
	)
	(:action light-off-1
		:parameters (?l - light ?t - temp)
		:precondition (and (light-is-on ?l) (temp-is-high ?t))
		:effect (and (not (light-is-on ?l)) (light-is-off ?l) (not (temp-is-high ?t)) (temp-is-ok ?t))
	)
	(:action light-off-2
		:parameters (?l - light ?t - temp)
		:precondition (and (light-is-on ?l) (temp-is-ok ?t))
		:effect (and (not (light-is-on ?l)) (light-is-off ?l) (not (temp-is-ok ?t)) (temp-is-low ?t))
	)
	(:action light-off-3
		:parameters (?l - light ?t - temp)
		:precondition (and (light-is-on ?l) (temp-is-low ?t))
		:effect (and (not (light-is-on ?l)) (light-is-off ?l))
	)
	(:action light-on-1
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-high ?t) (moisture-is-high ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (moisture-is-high ?m)) (moisture-is-ok ?m))
	)
	(:action light-on-2
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-high ?t) (moisture-is-ok ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (moisture-is-ok ?m)) (moisture-is-low ?m))
	)
	(:action light-on-3
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-high ?t) (moisture-is-low ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l))
	)
	(:action light-on-4
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-ok ?t) (moisture-is-high ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-ok ?t)) (temp-is-high ?t) (not (moisture-is-high ?m)) (moisture-is-ok ?m))
	)
	(:action light-on-5
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-ok ?t) (moisture-is-ok ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-ok ?t)) (temp-is-high ?t) (not (moisture-is-ok ?m)) (moisture-is-low ?m))
	)
	(:action light-on-6
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-ok ?t) (moisture-is-low ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-ok ?t)) (temp-is-high ?t))
	)
	(:action light-on-7
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-low ?t) (moisture-is-high ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-low ?t)) (temp-is-ok ?t) (not (moisture-is-high ?m)) (moisture-is-ok ?m))
	)
	(:action light-on-8
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-low ?t) (moisture-is-ok ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-low ?t)) (temp-is-ok ?t) (not (moisture-is-ok ?m)) (moisture-is-low ?m))
	)
	(:action light-on-9
		:parameters (?l - light ?t - temp ?m - moisture)
		:precondition (and (light-is-off ?l) (temp-is-low ?t) (moisture-is-low ?m))
		:effect (and (not (light-is-off ?l)) (light-is-on ?l) (not (temp-is-low ?t)) (temp-is-ok ?t))
	)
	(:action water-2
		:parameters (?m - moisture)
		:precondition (moisture-is-ok ?m)
		:effect (and (not (moisture-is-ok ?m)) (moisture-is-high ?m))
	)
	(:action water-3
		:parameters (?m - moisture)
		:precondition (moisture-is-low ?m)
		:effect (and (not (moisture-is-low ?m)) (moisture-is-ok ?m))
	)
)