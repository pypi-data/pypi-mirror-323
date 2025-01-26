The Survival Probability Adapted Nuclear Norm Shrinkage (SPANNS) Denoiser
=========================================================================

A simple denoiser compatible with VapourSynth.

Supported Formats
-----------------
The denoiser core supports any 2D numeric matrices. For VapourSynth usage, you need to provide clips with full precision and planes of the same dimensions (e.g., convert YUV422 to YUV444PS or RGBS first).

Usage
-----

`spanns.spanns(clip, ...)`

### Arguments:
- **clip** (*vs.VideoNode*): The original video node.
- **sigma** (*int*): Denoising strength. Default is `1`.
- **tol** (*float*): Noise tolerance in the range [0, 1]. Default is `0.7`.
- **gamma** (*float*): Texture threshold in the range [0, 1]. Higher values preserve less texture. Default is `0.5`.
- **passes** (*int*): Number of denoising steps. Default is `2`.
- **ref1** (*vs.VideoNode*): Reference clip, an approximation of the result. Default is a median filter.
- **ref2** (*vs.VideoNode*): Reference clip, a blurred one obtained from the original. It serves as an alternative way to control denoising strength. If provided, `sigma` will be ignored. Default is a box blur with radius equal to `sigma`.
- **planes** (*Sequence[int]*): Indices of planes to process. Default is `[0, 1, 2]`.

### Returns:
The denoised clip (*vs.VideoNode*).

TODO
----
- Implement GPU acceleration.

Background
----------
In 2019, the author was disappointed by the practical performance of WNNM, a well-regarded but (f\*\*\*\*\*\*)cumbersome denoising approach proposed years earlier. Although there have been improvements to the technique, most rely on patch matching and increasing complexity, which the author finds unappealing. Reflecting on its limitations, the author implemented a better (but still sh\*t) heuristic method: SPANNS.

In essence, SPANNS damps the orthogonal components according to the noise's survival probability along the axis of component magnitude (the singular values). While the denoising results might not stand out in today's advanced landscape, the author hopes someone can appreciate its simplicity.

Buy Me Coffee
-------------
Don't, I can't have coffee.
