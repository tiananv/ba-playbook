# Hand-authored checker fixture, not model output

## TC-001: Slots
Requirements: REQ-001
Given: A slot is available.
When: A visitor opens the slot list.
Then: The slot appears.

## TC-002: Cancellation
Requirements: REQ-002
Given: A booking is confirmed.
When: The visitor cancels it.

## TC-003: Referral
Requirements: REQ-003
Given: A new referral is ready to submit.
When: The referral is submitted.
Then: Its status is pending.

## TC-004: Missing link
Given: A visitor starts a booking.
When: The visitor chooses a service.
Then: The page shows the slots.

