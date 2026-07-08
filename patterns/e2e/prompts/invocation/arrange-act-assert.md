Write a unit test (Jest) for a shopping `Cart`: after adding two items and checking out, the cart total should be back to zero.
Our tests keep mixing setup with assertions and checking several things in one method, so failures are hard to read.
Write this test so the setup, the single action under test, and the checks are each their own clearly separated phase, and the test exercises exactly one behavior.
Show the test (assume `Cart`, `Item`, `add`, `checkout`, `total` exist).
