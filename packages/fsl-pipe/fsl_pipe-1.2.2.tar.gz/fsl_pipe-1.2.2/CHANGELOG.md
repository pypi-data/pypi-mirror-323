# Changelog
## [Unreleased]
## [v1.2.2]
### Fixed
- Job times are now integers even after scaling.
## [v1.2.1]
### Fixed
- Target file patterns now work from the CLI
- Fixed breaking bug of CLI in v1.2.0
## [v1.2.0]
### Added
- `--scale_jobtime` has been added to the command line and a new method `JobList.scale_jobtime` has been added. These allow all developer-set job times to be scaled by the user of a pipeline. A uniform scaling is applied to all jobs. This will only affect jobs submitted to the cluster.
- `clean_script` keyword added to `JobList.run()`. This allows one to keep the scripts submitted to the cluster even for jobs that succeeded by setting `JobList.run(clean_script="never")`. This feature is not available from the command line by default.
### Fixed
- Setting target file patterns now works as intended.
- `--pipeline_method` is not `--pipeline-method` to make it more consistend with the other command line arguments.
## [v1.1.3]
### Fixed
- Fixed breaking import of console when printing rich output
## [v1.1.2]
### Changed
- Use [`uv`](https://docs.astral.sh/uv/) for project management (i.e., manage dependencies, testing, building, and publishing).
### Fixed
- Support file-tree to have multiple templates with the same key as long as that key is not used in the pipeline
## [v1.1.1]
### Fixed
- Allow `Var` to be used for placholders with a singular value.
## [v1.1.0]
### Added
- `JobList.split_pipeline` has been added to split a pipeline into independent stages based on labels and/or submit parameters. This can be called after `generate_jobs`.
### Changed
- Jobs in `JobList` are now guaranteed to be sorted (i.e., any job will always be listed after its dependencies).
### Fixed
- Fixed bug where pipeline would crash if some of the placeholder values were None.
- Removed confusing warning messages when running `.filter(None)` on a joblist containing `Ref` or `In` files.
- Batching a pipeline no longer breaks the original, unbatched pipeline
## [v1.0.3]
### Fixed
- Using the `dask` backend now works.
- If multiple placeholders were passed on to a function (using `no_iter=True`), there would be a hashing error if they are stored as a list. This will no longer occur.
## [v1.0.2]
### Changed
- Moved the fsl-pipe code and documentation from the ndcn0236 to the FSL namespace in gitlab
## [v1.0.1]
### Fixed
- Improved support for [linked placeholder values](https://open.win.ox.ac.uk/pages/fsl/file-tree/tutorial.html#linked-placholder-values). Previously, these would sometimes lead to crashes, when multiple conflicting jobs were created.

[Unreleased]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.2.2...main
[v1.2.2]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.2.1...v1.2.2
[v1.2.1]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.2.0...v1.2.1
[v1.2.0]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.1.3...v1.2.0
[v1.1.3]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.1.2...v1.1.3
[v1.1.2]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.1.1...v1.1.2
[v1.1.1]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.1.0...v1.1.1
[v1.1.0]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.0.3...v1.1.0
[v1.0.3]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.0.2...v1.0.3
[v1.0.2]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.0.1...v1.0.2
[v1.0.1]: https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/compare/v1.0.0...v1.0.1