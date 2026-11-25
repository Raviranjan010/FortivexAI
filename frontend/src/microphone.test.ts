import {expect, it} from 'vitest';
import {signalLevel} from './microphone';

it('maps measured signal energy to a bounded meter', () => {
  expect(signalLevel(new Float32Array())).toBe(0);
  expect(signalLevel(new Float32Array([0, 0]))).toBe(0);
  expect(signalLevel(new Float32Array([0.125, -0.125]))).toBe(0.5);
  expect(signalLevel(new Float32Array([1, -1]))).toBe(1);
});
