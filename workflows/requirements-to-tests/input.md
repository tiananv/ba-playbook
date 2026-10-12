# Paper Lantern Community Clinic: agreed requirements for the exercise

Fictional training case. This is an author-written input baseline, not an AI
output or evidence of real stakeholder agreement. It describes booking administration.

## REQ-001: Available slots

After a visitor chooses a service, the page must show only available slots for that
service. If none are available, show a clear no-slots message.

## REQ-002: Competing bookings

Only one booking may be confirmed for a slot. If another visitor confirms it first,
tell the unsuccessful visitor the slot is gone and offer a fresh slot selection.

## REQ-003: Referral status

A newly submitted referral must start in pending status. Only a coordinator may
record an administrative review that moves it to ready or needs information.
The booking page must not infer clinical suitability from this status.

## REQ-004: Cancellation

Cancelling a confirmed booking must display a cancellation reference and make the
slot available again. No reminder or retention rule is agreed in this exercise.

