import {describe,it,expect} from 'vitest';import {canTransition} from './voice';
describe('voice state machine',()=>{it('blocks overlapping processing',()=>{expect(canTransition('PROCESSING','PROCESSING')).toBe(false)});it('pauses listening for processing',()=>{expect(canTransition('LISTENING','PROCESSING')).toBe(true);expect(canTransition('SPEAKING','LISTENING')).toBe(true)})})
