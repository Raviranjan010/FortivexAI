export function signalLevel(samples: Float32Array): number {
  const energy = samples.reduce((sum, sample) => sum + sample * sample, 0);
  return samples.length ? Math.min(1, Math.sqrt(energy / samples.length) * 4) : 0;
}

export function monitorMicrophone(onLevel: (level: number) => void, onError: () => void) {
  let disposed = false;
  let stream: MediaStream | undefined;
  let context: AudioContext | undefined;
  let frame = 0;
  const stop = () => {
    disposed = true;
    cancelAnimationFrame(frame);
    stream?.getTracks().forEach(track => track.stop());
    if (context && context.state !== 'closed') void context.close().catch(() => {});
  };
  async function start() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({audio: true});
      if (disposed) { stream.getTracks().forEach(track => track.stop()); return; }
      context = new AudioContext();
      const analyser = context.createAnalyser();
      context.createMediaStreamSource(stream).connect(analyser);
      await context.resume();
      const samples = new Float32Array(analyser.fftSize);
      const render = () => {
        if (disposed) return;
        analyser.getFloatTimeDomainData(samples);
        onLevel(signalLevel(samples));
        frame = requestAnimationFrame(render);
      };
      render();
    } catch {
      if (!disposed) onError();
      stop();
    }
  }
  void start();
  return stop;
}
