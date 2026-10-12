# Paper Lantern Community Clinic: booking and referral specification

Fictional training case. Author-written input, not a model output. This draft
describes administration only and contains open design questions.

## SEC-001: Choose a service and a slot

The visitor chooses a service, then sees available appointment slots. A slot has a
service, start time and availability state. The booking journey must work on a
keyboard. The page shows a clear message if no slots are available.

## SEC-002: Confirm a booking

The system creates a booking and displays a confirmation reference. Only one
booking may be confirmed for a slot. The page may retry after a connection error.
The reservation timeout is an open decision.

## SEC-003: Referral administration

A referral starts in pending status. A coordinator can record an administrative
review and change its status to ready or needs information. This status does not
express clinical suitability. The page displays a referral status to the visitor.

## SEC-004: Cancel a booking

The visitor can cancel a confirmed booking. The page displays a cancellation
reference and makes the slot available again. The notification channel is an
open decision.

## SEC-005: Decisions and release

The service owner must agree unresolved rules before release. Retention, access
permissions and the treatment of repeated submissions need decisions. This draft
sets no legal, clinical or regulatory requirements.

