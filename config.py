from torch import roll
from environment.sumoenv import default_sumoenv_config
from ray.rllib.agents.dqn import DEFAULT_CONFIG
from ray.rllib.utils.typing import TrainerConfigDict
from ray.rllib.agents.trainer import Trainer
from ray.rllib.models import MODEL_DEFAULTS
from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.evaluation.collectors.simple_list_collector import SimpleListCollector
from ray.rllib.utils.deprecation import (
    DEPRECATED_VALUE,
)
from sys import platform

env_config = default_sumoenv_config.copy()
if platform == "linux" or platform == "linux2":

    print('Platform Linux')

    num_workers = 4
    num_envs_per_worker = 1
    evaluation_interval = 10
    num_cpus_per_worker = 2
    num_gpus = 1

elif platform == "win32":
    # Windows...
    print('Platform Windows')
    num_workers = 1
    num_envs_per_worker = 1
    evaluation_interval = 0
    num_gpus = 0
    num_cpus_per_worker = 1
    env_config['sumo_bin'] = 'sumo-gui'



# config changes

batch_mode = 'truncate_episodes'
lr = 0.001
lr_schedule = None
horizon = 551
framework = 'torch'
exploration_type = 'EpsilonGreedy'
evaluation_interval = 0
evaluation_duration = 1
evaluation_num_workers = 0
compress_observations = False


num_gpus_per_worker = num_gpus / (num_workers +1)
simple_optimizer = True
epsilon_timesteps = 10000

env_config_eval = default_sumoenv_config.copy()
env_config_eval['evaluate'] = True
evaluation_config = {
        # Example: overriding env_config, exploration, etc:
        "env_config": env_config_eval,
        "explore": False
    }
timesteps_per_iteration = (horizon  +1)* num_envs_per_worker * num_workers
replay_buffer_config_capacity = 50000
replay_buffer_config_batch = 32


rollout_fragment_length = 4
train_batch_size = 32


CONFIG: TrainerConfigDict = {
    # === Settings for Rollout Worker processes ===
    # Number of rollout worker actors to create for parallel sampling. Setting
    # this to 0 will force rollouts to be done in the trainer actor.
    "num_workers": num_workers,
    # Number of environments to evaluate vector-wise per worker. This enables
    # model inference batching, which can improve performance for inference
    # bottlenecked workloads.
    "num_envs_per_worker": num_envs_per_worker,
    # When `num_workers` > 0, the driver (local_worker; worker-idx=0) does not
    # need an environment. This is because it doesn't have to sample (done by
    # remote_workers; worker_indices > 0) nor evaluate (done by evaluation
    # workers; see below).
    "create_env_on_driver": False,
    # Divide episodes into fragments of this many steps each during rollouts.
    # Sample batches of this size are collected from rollout workers and
    # combined into a larger batch of `train_batch_size` for learning.
    #
    # For example, given rollout_fragment_length=100 and train_batch_size=1000:
    #   1. RLlib collects 10 fragments of 100 steps each from rollout workers.
    #   2. These fragments are concatenated and we perform an epoch of SGD.
    #
    # When using multiple envs per worker, the fragment size is multiplied by
    # `num_envs_per_worker`. This is since we are collecting steps from
    # multiple envs in parallel. For example, if num_envs_per_worker=5, then
    # rollout workers will return experiences in chunks of 5*100 = 500 steps.
    #
    # The dataflow here can vary per algorithm. For example, PPO further
    # divides the train batch into minibatches for multi-epoch SGD.
    "rollout_fragment_length": rollout_fragment_length,
    # How to build per-Sampler (RolloutWorker) batches, which are then
    # usually concat'd to form the train batch. Note that "steps" below can
    # mean different things (either env- or agent-steps) and depends on the
    # `count_steps_by` (multiagent) setting below.
    # truncate_episodes: Each produced batch (when calling
    #   RolloutWorker.sample()) will contain exactly `rollout_fragment_length`
    #   steps. This mode guarantees evenly sized batches, but increases
    #   variance as the future return must now be estimated at truncation
    #   boundaries.
    # complete_episodes: Each unroll happens exactly over one episode, from
    #   beginning to end. Data collection will not stop unless the episode
    #   terminates or a configured horizon (hard or soft) is hit.
    "batch_mode": batch_mode,

    # === Settings for the Trainer process ===
    # Discount factor of the MDP.
    "gamma": 0.99,
    # The default learning rate.
    "lr": lr,
    # Training batch size, if applicable. Should be >= rollout_fragment_length.
    # Samples batches will be concatenated together to a batch of this size,
    # which is then passed to SGD.
    "train_batch_size": train_batch_size,
    # Arguments to pass to the policy model. See models/catalog.py for a full
    # list of the available model options.
    "model": MODEL_DEFAULTS,
    # Arguments to pass to the policy optimizer. These vary by optimizer.
    "optimizer": {},

    # === Environment Settings ===
    # Number of steps after which the episode is forced to terminate. Defaults
    # to `env.spec.max_episode_steps` (if present) for Gym envs.
    "horizon": horizon,
    # Calculate rewards but don't reset the environment when the horizon is
    # hit. This allows value estimation and RNN state to span across logical
    # episodes denoted by horizon. This only has an effect if horizon != inf.
    "soft_horizon": False,
    # Don't set 'done' at the end of the episode.
    # In combination with `soft_horizon`, this works as follows:
    # - no_done_at_end=False soft_horizon=False:
    #   Reset env and add `done=True` at end of each episode.
    # - no_done_at_end=True soft_horizon=False:
    #   Reset env, but do NOT add `done=True` at end of the episode.
    # - no_done_at_end=False soft_horizon=True:
    #   Do NOT reset env at horizon, but add `done=True` at the horizon
    #   (pretending the episode has terminated).
    # - no_done_at_end=True soft_horizon=True:
    #   Do NOT reset env at horizon and do NOT add `done=True` at the horizon.
    "no_done_at_end": False,
    # The environment specifier:
    # This can either be a tune-registered env, via
    # `tune.register_env([name], lambda env_ctx: [env object])`,
    # or a string specifier of an RLlib supported type. In the latter case,
    # RLlib will try to interpret the specifier as either an openAI gym env,
    # a PyBullet env, a ViZDoomGym env, or a fully qualified classpath to an
    # Env class, e.g. "ray.rllib.examples.env.random_env.RandomEnv".
    "env": None,
    # The observation- and action spaces for the Policies of this Trainer.
    # Use None for automatically inferring these from the given env.
    "observation_space": None,
    "action_space": None,
    # Arguments dict passed to the env creator as an EnvContext object (which
    # is a dict plus the properties: num_workers, worker_index, vector_index,
    # and remote).
    "env_config": env_config,
    # If using num_envs_per_worker > 1, whether to create those new envs in
    # remote processes instead of in the same worker. This adds overheads, but
    # can make sense if your envs can take much time to step / reset
    # (e.g., for StarCraft). Use this cautiously; overheads are significant.
    "remote_worker_envs": False,
    # Timeout that remote workers are waiting when polling environments.
    # 0 (continue when at least one env is ready) is a reasonable default,
    # but optimal value could be obtained by measuring your environment
    # step / reset and model inference perf.
    "remote_env_batch_wait_ms": 0,
    # A callable taking the last train results, the base env and the env
    # context as args and returning a new task to set the env to.
    # The env must be a `TaskSettableEnv` sub-class for this to work.
    # See `examples/curriculum_learning.py` for an example.
    "env_task_fn": None,
    # If True, try to render the environment on the local worker or on worker
    # 1 (if num_workers > 0). For vectorized envs, this usually means that only
    # the first sub-environment will be rendered.
    # In order for this to work, your env will have to implement the
    # `render()` method which either:
    # a) handles window generation and rendering itself (returning True) or
    # b) returns a numpy uint8 image of shape [height x width x 3 (RGB)].
    "render_env": False,
    # If True, stores videos in this relative directory inside the default
    # output dir (~/ray_results/...). Alternatively, you can specify an
    # absolute path (str), in which the env recordings should be
    # stored instead.
    # Set to False for not recording anything.
    # Note: This setting replaces the deprecated `monitor` key.
    "record_env": False,
    # Whether to clip rewards during Policy's postprocessing.
    # None (default): Clip for Atari only (r=sign(r)).
    # True: r=sign(r): Fixed rewards -1.0, 1.0, or 0.0.
    # False: Never clip.
    # [float value]: Clip at -value and + value.
    # Tuple[value1, value2]: Clip at value1 and value2.
    "clip_rewards": None,
    # If True, RLlib will learn entirely inside a normalized action space
    # (0.0 centered with small stddev; only affecting Box components).
    # We will unsquash actions (and clip, just in case) to the bounds of
    # the env's action space before sending actions back to the env.
    "normalize_actions": True,
    # If True, RLlib will clip actions according to the env's bounds
    # before sending them back to the env.
    # TODO: (sven) This option should be obsoleted and always be False.
    "clip_actions": False,
    # Whether to use "rllib" or "deepmind" preprocessors by default
    # Set to None for using no preprocessor. In this case, the model will have
    # to handle possibly complex observations from the environment.
    "preprocessor_pref": "deepmind",

    # === Debug Settings ===
    # Set the ray.rllib.* log level for the agent process and its workers.
    # Should be one of DEBUG, INFO, WARN, or ERROR. The DEBUG level will also
    # periodically print out summaries of relevant internal dataflow (this is
    # also printed out once at startup at the INFO level). When using the
    # `rllib train` command, you can also use the `-v` and `-vv` flags as
    # shorthand for INFO and DEBUG.
    "log_level": "WARN",
    # Callbacks that will be run during various phases of training. See the
    # `DefaultCallbacks` class and `examples/custom_metrics_and_callbacks.py`
    # for more usage information.
    "callbacks": DefaultCallbacks,
    # Whether to attempt to continue training if a worker crashes. The number
    # of currently healthy workers is reported as the "num_healthy_workers"
    # metric.
    "ignore_worker_failures": False,
    # Whether - upon a worker failure - RLlib will try to recreate the lost worker as
    # an identical copy of the failed one. The new worker will only differ from the
    # failed one in its `self.recreated_worker=True` property value. It will have
    # the same `worker_index` as the original one.
    # If True, the `ignore_worker_failures` setting will be ignored.
    "recreate_failed_workers": False,
    # Log system resource metrics to results. This requires `psutil` to be
    # installed for sys stats, and `gputil` for GPU metrics.
    "log_sys_usage": True,
    # Use fake (infinite speed) sampler. For testing only.
    "fake_sampler": False,

    # === Deep Learning Framework Settings ===
    # tf: TensorFlow (static-graph)
    # tf2: TensorFlow 2.x (eager or traced, if eager_tracing=True)
    # tfe: TensorFlow eager (or traced, if eager_tracing=True)
    # torch: PyTorch
    "framework": framework,
    # Enable tracing in eager mode. This greatly improves performance
    # (speedup ~2x), but makes it slightly harder to debug since Python
    # code won't be evaluated after the initial eager pass.
    # Only possible if framework=[tf2|tfe].
    "eager_tracing": False,
    # Maximum number of tf.function re-traces before a runtime error is raised.
    # This is to prevent unnoticed retraces of methods inside the
    # `..._eager_traced` Policy, which could slow down execution by a
    # factor of 4, without the user noticing what the root cause for this
    # slowdown could be.
    # Only necessary for framework=[tf2|tfe].
    # Set to None to ignore the re-trace count and never throw an error.
    "eager_max_retraces": 20,

    # === Exploration Settings ===
    # Default exploration behavior, iff `explore`=None is passed into
    # compute_action(s).
    # Set to False for no exploration behavior (e.g., for evaluation).
    "explore": True,
    # Provide a dict specifying the Exploration object's config.
    "exploration_config": {
        # The Exploration class to use. In the simplest case, this is the name
        # (str) of any class present in the `rllib.utils.exploration` package.
        # You can also provide the python class directly or the full location
        # of your class (e.g. "ray.rllib.utils.exploration.epsilon_greedy.
        # EpsilonGreedy").
        "type": exploration_type,
        # Add constructor kwargs here (if any).
    },
    # === Evaluation Settings ===
    # Evaluate with every `evaluation_interval` training iterations.
    # The evaluation stats will be reported under the "evaluation" metric key.
    # Note that for Ape-X metrics are already only reported for the lowest
    # epsilon workers (least random workers).
    # Set to None (or 0) for no evaluation.
    "evaluation_interval": evaluation_interval,
    # Duration for which to run evaluation each `evaluation_interval`.
    # The unit for the duration can be set via `evaluation_duration_unit` to
    # either "episodes" (default) or "timesteps".
    # If using multiple evaluation workers (evaluation_num_workers > 1),
    # the load to run will be split amongst these.
    # If the value is "auto":
    # - For `evaluation_parallel_to_training=True`: Will run as many
    #   episodes/timesteps that fit into the (parallel) training step.
    # - For `evaluation_parallel_to_training=False`: Error.
    "evaluation_duration": evaluation_duration,
    # The unit, with which to count the evaluation duration. Either "episodes"
    # (default) or "timesteps".
    "evaluation_duration_unit": "episodes",
    # Whether to run evaluation in parallel to a Trainer.train() call
    # using threading. Default=False.
    # E.g. evaluation_interval=2 -> For every other training iteration,
    # the Trainer.train() and Trainer.evaluate() calls run in parallel.
    # Note: This is experimental. Possible pitfalls could be race conditions
    # for weight synching at the beginning of the evaluation loop.
    "evaluation_parallel_to_training": False,
    # Internal flag that is set to True for evaluation workers.
    "in_evaluation": False,
    # Typical usage is to pass extra args to evaluation env creator
    # and to disable exploration by computing deterministic actions.
    # IMPORTANT NOTE: Policy gradient algorithms are able to find the optimal
    # policy, even if this is a stochastic one. Setting "explore=False" here
    # will result in the evaluation workers not using this optimal policy!
    # "evaluation_config": {
    #     # Example: overriding env_config, exploration, etc:
    #     # "env_config": {...},
    #     # "explore": False
    # },

    # === Replay Buffer Settings ===
    # Provide a dict specifying the ReplayBuffer's config.
    # "replay_buffer_config": {
    #     The ReplayBuffer class to use. Any class that obeys the
    #     ReplayBuffer API can be used here. In the simplest case, this is the
    #     name (str) of any class present in the `rllib.utils.replay_buffers`
    #     package. You can also provide the python class directly or the
    #     full location of your class (e.g.
    #     "ray.rllib.utils.replay_buffers.replay_buffer.ReplayBuffer").
    #     "type": "ReplayBuffer",
    #     The capacity of units that can be stored in one ReplayBuffer
    #     instance before eviction.
    #     "capacity": 10000,
    #     Specifies how experiences are stored. Either 'sequences' or
    #     'timesteps'.
    #     "storage_unit": "timesteps",
    #     Add constructor kwargs here (if any).
    # },

    # Number of parallel workers to use for evaluation. Note that this is set
    # to zero by default, which means evaluation will be run in the trainer
    # process (only if evaluation_interval is not None). If you increase this,
    # it will increase the Ray resource usage of the trainer since evaluation
    # workers are created separately from rollout workers (used to sample data
    # for training).
    "evaluation_num_workers": evaluation_num_workers,
    # Customize the evaluation method. This must be a function of signature
    # (trainer: Trainer, eval_workers: WorkerSet) -> metrics: dict. See the
    # Trainer.evaluate() method to see the default implementation.
    # The Trainer guarantees all eval workers have the latest policy state
    # before this function is called.
    "custom_eval_function": None,
    # Make sure the latest available evaluation results are always attached to
    # a step result dict.
    # This may be useful if Tune or some other meta controller needs access
    # to evaluation metrics all the time.
    "always_attach_evaluation_results": False,
    # Store raw custom metrics without calculating max, min, mean
    "keep_per_episode_custom_metrics": False,

    # === Advanced Rollout Settings ===
    # Use a background thread for sampling (slightly off-policy, usually not
    # advisable to turn on unless your env specifically requires it).
    "sample_async": False,

    # The SampleCollector class to be used to collect and retrieve
    # environment-, model-, and sampler data. Override the SampleCollector base
    # class to implement your own collection/buffering/retrieval logic.
    "sample_collector": SimpleListCollector,

    # Element-wise observation filter, either "NoFilter" or "MeanStdFilter".
    "observation_filter": "NoFilter",
    # Whether to synchronize the statistics of remote filters.
    "synchronize_filters": True,
    # Configures TF for single-process operation by default.
    "tf_session_args": {
        # note: overridden by `local_tf_session_args`
        "intra_op_parallelism_threads": 2,
        "inter_op_parallelism_threads": 2,
        "gpu_options": {
            "allow_growth": True,
        },
        "log_device_placement": False,
        "device_count": {
            "CPU": 1
        },
        # Required by multi-GPU (num_gpus > 1).
        "allow_soft_placement": True,
    },
    # Override the following tf session args on the local worker
    "local_tf_session_args": {
        # Allow a higher level of parallelism by default, but not unlimited
        # since that can cause crashes with many concurrent drivers.
        "intra_op_parallelism_threads": 8,
        "inter_op_parallelism_threads": 8,
    },
    # Whether to LZ4 compress individual observations.
    "compress_observations": compress_observations,
    # "compress_observations": False,
    # Wait for metric batches for at most this many seconds. Those that
    # have not returned in time will be collected in the next train iteration.
    "metrics_episode_collection_timeout_s": 180,
    # Smooth metrics over this many episodes.
    "metrics_num_episodes_for_smoothing": 100,
    # Minimum time interval to run one `train()` call for:
    # If - after one `step_attempt()`, this time limit has not been reached,
    # will perform n more `step_attempt()` calls until this minimum time has
    # been consumed. Set to None or 0 for no minimum time.
    "min_time_s_per_reporting": None,
    # Minimum train/sample timesteps to optimize for per `train()` call.
    # This value does not affect learning, only the length of train iterations.
    # If - after one `step_attempt()`, the timestep counts (sampling or
    # training) have not been reached, will perform n more `step_attempt()`
    # calls until the minimum timesteps have been executed.
    # Set to None or 0 for no minimum timesteps.
    "min_train_timesteps_per_reporting": None,
    "min_sample_timesteps_per_reporting": None,

    # This argument, in conjunction with worker_index, sets the random seed of
    # each worker, so that identically configured trials will have identical
    # results. This makes experiments reproducible.
    "seed": None,
    # Any extra python env vars to set in the trainer process, e.g.,
    # {"OMP_NUM_THREADS": "16"}
    "extra_python_environs_for_driver": {},
    # The extra python environments need to set for worker processes.
    "extra_python_environs_for_worker": {},

    # === Resource Settings ===
    # Number of GPUs to allocate to the trainer process. Note that not all
    # algorithms can take advantage of trainer GPUs. Support for multi-GPU
    # is currently only available for tf-[PPO/IMPALA/DQN/PG].
    # This can be fractional (e.g., 0.3 GPUs).
    "num_gpus": num_gpus,
    # Set to True for debugging (multi-)?GPU funcitonality on a CPU machine.
    # GPU towers will be simulated by graphs located on CPUs in this case.
    # Use `num_gpus` to test for different numbers of fake GPUs.
    "_fake_gpus": False,
    # Number of CPUs to allocate per worker.
    "num_cpus_per_worker": num_cpus_per_worker,
    # Number of GPUs to allocate per worker. This can be fractional. This is
    # usually needed only if your env itself requires a GPU (i.e., it is a
    # GPU-intensive video game), or model inference is unusually expensive.
    "num_gpus_per_worker": num_gpus_per_worker,
    # Any custom Ray resources to allocate per worker.
    "custom_resources_per_worker": {},
    # Number of CPUs to allocate for the trainer. Note: this only takes effect
    # when running in Tune. Otherwise, the trainer runs in the main program.
    "num_cpus_for_driver": 1,
    # The strategy for the placement group factory returned by
    # `Trainer.default_resource_request()`. A PlacementGroup defines, which
    # devices (resources) should always be co-located on the same node.
    # For example, a Trainer with 2 rollout workers, running with
    # num_gpus=1 will request a placement group with the bundles:
    # [{"gpu": 1, "cpu": 1}, {"cpu": 1}, {"cpu": 1}], where the first bundle is
    # for the driver and the other 2 bundles are for the two workers.
    # These bundles can now be "placed" on the same or different
    # nodes depending on the value of `placement_strategy`:
    # "PACK": Packs bundles into as few nodes as possible.
    # "SPREAD": Places bundles across distinct nodes as even as possible.
    # "STRICT_PACK": Packs bundles into one node. The group is not allowed
    #   to span multiple nodes.
    # "STRICT_SPREAD": Packs bundles across distinct nodes.
    # "placement_strategy": "PACK",
    "placement_strategy": "PACK",

    # TODO(jungong, sven): we can potentially unify all input types
    #     under input and input_config keys. E.g.
    #     input: sample
    #     input_config {
    #         env: Cartpole-v0
    #     }
    #     or:
    #     input: json_reader
    #     input_config {
    #         path: /tmp/
    #     }
    #     or:
    #     input: dataset
    #     input_config {
    #         format: parquet
    #         path: /tmp/
    #     }
    # === Offline Datasets ===
    # Specify how to generate experiences:
    #  - "sampler": Generate experiences via online (env) simulation (default).
    #  - A local directory or file glob expression (e.g., "/tmp/*.json").
    #  - A list of individual file paths/URIs (e.g., ["/tmp/1.json",
    #    "s3://bucket/2.json"]).
    #  - A dict with string keys and sampling probabilities as values (e.g.,
    #    {"sampler": 0.4, "/tmp/*.json": 0.4, "s3://bucket/expert.json": 0.2}).
    #  - A callable that takes an `IOContext` object as only arg and returns a
    #    ray.rllib.offline.InputReader.
    #  - A string key that indexes a callable with tune.registry.register_input
    "input": "sampler",
    # Arguments accessible from the IOContext for configuring custom input
    "input_config": {},
    # True, if the actions in a given offline "input" are already normalized
    # (between -1.0 and 1.0). This is usually the case when the offline
    # file has been generated by another RLlib algorithm (e.g. PPO or SAC),
    # while "normalize_actions" was set to True.
    "actions_in_input_normalized": False,
    # Specify how to evaluate the current policy. This only has an effect when
    # reading offline experiences ("input" is not "sampler").
    # Available options:
    #  - "wis": the weighted step-wise importance sampling estimator.
    #  - "is": the step-wise importance sampling estimator.
    #  - "simulation": run the environment in the background, but use
    #    this data for evaluation only and not for learning.
    "input_evaluation": ["is", "wis"],
    # Whether to run postprocess_trajectory() on the trajectory fragments from
    # offline inputs. Note that postprocessing will be done using the *current*
    # policy, not the *behavior* policy, which is typically undesirable for
    # on-policy algorithms.
    "postprocess_inputs": False,
    # If positive, input batches will be shuffled via a sliding window buffer
    # of this number of batches. Use this if the input data is not in random
    # enough order. Input is delayed until the shuffle buffer is filled.
    "shuffle_buffer_size": 0,
    # Specify where experiences should be saved:
    #  - None: don't save any experiences
    #  - "logdir" to save to the agent log dir
    #  - a path/URI to save to a custom output directory (e.g., "s3://bucket/")
    #  - a function that returns a rllib.offline.OutputWriter
    "output": None,
    # Arguments accessible from the IOContext for configuring custom output
    "output_config": {},
    # What sample batch columns to LZ4 compress in the output data.
    "output_compress_columns": ["obs", "new_obs"],
    # Max output file size (in bytes) before rolling over to a new file.
    "output_max_file_size": 64 * 1024 * 1024,

    # === Settings for Multi-Agent Environments ===
    "multiagent": {
        # Map of type MultiAgentPolicyConfigDict from policy ids to tuples
        # of (policy_cls, obs_space, act_space, config). This defines the
        # observation and action spaces of the policies and any extra config.
        "policies": {},
        # Keep this many policies in the "policy_map" (before writing
        # least-recently used ones to disk/S3).
        "policy_map_capacity": 100,
        # Where to store overflowing (least-recently used) policies?
        # Could be a directory (str) or an S3 location. None for using
        # the default output dir.
        "policy_map_cache": None,
        # Function mapping agent ids to policy ids.
        "policy_mapping_fn": None,
        # Determines those policies that should be updated.
        # Options are:
        # - None, for all policies.
        # - An iterable of PolicyIDs that should be updated.
        # - A callable, taking a PolicyID and a SampleBatch or MultiAgentBatch
        #   and returning a bool (indicating whether the given policy is trainable
        #   or not, given the particular batch). This allows you to have a policy
        #   trained only on certain data (e.g. when playing against a certain
        #   opponent).
        "policies_to_train": None,
        # Optional function that can be used to enhance the local agent
        # observations to include more state.
        # See rllib/evaluation/observation_function.py for more info.
        "observation_fn": None,
        # When replay_mode=lockstep, RLlib will replay all the agent
        # transitions at a particular timestep together in a batch. This allows
        # the policy to implement differentiable shared computations between
        # agents it controls at that timestep. When replay_mode=independent,
        # transitions are replayed independently per policy.
        "replay_mode": "independent",
        # Which metric to use as the "batch size" when building a
        # MultiAgentBatch. The two supported values are:
        # env_steps: Count each time the env is "stepped" (no matter how many
        #   multi-agent actions are passed/how many multi-agent observations
        #   have been returned in the previous step).
        # agent_steps: Count each individual agent step as one step.
        "count_steps_by": "env_steps",
    },

    # === Logger ===
    # Define logger-specific configuration to be used inside Logger
    # Default value None allows overwriting with nested dicts
    "logger_config": None,

    # === API deprecations/simplifications/changes ===
    # Experimental flag.
    # If True, TFPolicy will handle more than one loss/optimizer.
    # Set this to True, if you would like to return more than
    # one loss term from your `loss_fn` and an equal number of optimizers
    # from your `optimizer_fn`.
    # In the future, the default for this will be True.
    "_tf_policy_handles_more_than_one_loss": False,
    # Experimental flag.
    # If True, no (observation) preprocessor will be created and
    # observations will arrive in model as they are returned by the env.
    # In the future, the default for this will be True.
    "_disable_preprocessor_api": False,
    # Experimental flag.
    # If True, RLlib will no longer flatten the policy-computed actions into
    # a single tensor (for storage in SampleCollectors/output files/etc..),
    # but leave (possibly nested) actions as-is. Disabling flattening affects:
    # - SampleCollectors: Have to store possibly nested action structs.
    # - Models that have the previous action(s) as part of their input.
    # - Algorithms reading from offline files (incl. action information).
    "_disable_action_flattening": False,
    # Experimental flag.
    # If True, the execution plan API will not be used. Instead,
    # a Trainer's `training_iteration` method will be called as-is each
    # training iteration.
    "_disable_execution_plan_api": False,

    # If True, disable the environment pre-checking module.
    "disable_env_checking": False,

    # === Deprecated keys ===
    # Uses the sync samples optimizer instead of the multi-gpu one. This is
    # usually slower, but you might want to try it if you run into issues with
    # the default optimizer.
    # This will be set automatically from now on.
    "simple_optimizer": simple_optimizer,
    # "simple_optimizer": DEPRECATED_VALUE,
    # Whether to write episode stats and videos to the agent log dir. This is
    # typically located in ~/ray_results.
    "monitor": DEPRECATED_VALUE,
    # Replaced by `evaluation_duration=10` and
    # `evaluation_duration_unit=episodes`.
    "evaluation_num_episodes": DEPRECATED_VALUE,
    # Use `metrics_num_episodes_for_smoothing` instead.
    "metrics_smoothing_episodes": DEPRECATED_VALUE,
    # Use `min_[env|train]_timesteps_per_reporting` instead.
    "timesteps_per_iteration": 0,
    # Use `min_time_s_per_reporting` instead.
    "min_iter_time_s": DEPRECATED_VALUE,
    # Use `metrics_episode_collection_timeout_s` instead.
    "collect_metrics_timeout": DEPRECATED_VALUE,
    # === Exploration Settings ===
    "exploration_config": {
        # The Exploration class to use.
        "type": "EpsilonGreedy",
        "type": exploration_type,
        # Config for the Exploration class' constructor:
        "initial_epsilon": 1.0,
        "final_epsilon": 0.02,
        "epsilon_timesteps": epsilon_timesteps,  # Timesteps over which to anneal epsilon.
        # "epsilon_timesteps": 10000,  # Timesteps over which to anneal epsilon.

        # For soft_q, use:
        # "exploration_config" = {
        #   "type": "SoftQ"
        #   "temperature": [float, e.g. 1.0]
        # }
    },
    # Switch to greedy actions in evaluation workers.
    # "evaluation_config": {
    #     "explore": False,
    # },
    "evaluation_config": evaluation_config,

    # Minimum env steps to optimize for per train call. This value does
    # not affect learning, only the length of iterations.
    "timesteps_per_iteration": timesteps_per_iteration,
    # Update the target network every `target_network_update_freq` steps.
    "target_network_update_freq": 500,

    # === Replay buffer ===
    # Size of the replay buffer. Note that if async_updates is set, then
    # each worker will have a replay buffer of this size.
    "buffer_size": DEPRECATED_VALUE,
    # The following values have moved because of the new ReplayBuffer API
    "prioritized_replay": DEPRECATED_VALUE,
    "learning_starts": DEPRECATED_VALUE,
    "replay_batch_size": DEPRECATED_VALUE,
    "replay_sequence_length": DEPRECATED_VALUE,
    "prioritized_replay_alpha": DEPRECATED_VALUE,
    "prioritized_replay_beta": DEPRECATED_VALUE,
    "prioritized_replay_eps": DEPRECATED_VALUE,
    "replay_buffer_config": {
        # Use the new ReplayBuffer API here
        "_enable_replay_buffer_api": True,
        # How many steps of the model to sample before learning starts.
        "learning_starts": 1000,
        "type": "MultiAgentReplayBuffer",
        "capacity": replay_buffer_config_capacity,
        "replay_batch_size": replay_buffer_config_batch,
        # The number of contiguous environment steps to replay at once. This
        # may be set to greater than 1 to support recurrent models.
        "replay_sequence_length": 1,
    },
    # Set this to True, if you want the contents of your buffer(s) to be
    # stored in any saved checkpoints as well.
    # Warnings will be created if:
    # - This is True AND restoring from a checkpoint that contains no buffer
    #   data.
    # - This is False AND restoring from a checkpoint that does contain
    #   buffer data.
    "store_buffer_in_checkpoints": False,

    # === Optimization ===
    # Learning rate for adam optimizer
    "lr": lr,
    # Learning rate schedule.
    # In the format of [[timestep, value], [timestep, value], ...]
    # A schedule should normally start from timestep 0.
    # "lr_schedule": None,
    "lr_schedule": lr_schedule,
    # Adam epsilon hyper parameter
    "adam_epsilon": 1e-8,
    # If not None, clip gradients during optimization at this value
    "grad_clip": 40,
    # Update the replay buffer with this many samples at once. Note that
    # this setting applies per-worker if num_workers > 1.
    "rollout_fragment_length": 4,
    # Size of a batch sampled from replay buffer for training. Note that
    # if async_updates is set, then each worker returns gradients for a
    # batch of this size.
    "train_batch_size": train_batch_size,

    # === Parallelism ===
    # Number of workers for collecting samples with. This only makes sense
    # to increase if your environment is particularly slow to sample, or if
    # you"re using the Async or Ape-X optimizers.
    "num_workers": num_workers,
    # Prevent reporting frequency from going lower than this time span.
    "min_time_s_per_reporting": 1,

    # Experimental flag.
    # If True, the execution plan API will not be used. Instead,
    # a Trainer's `training_iteration` method will be called as-is each
    # training iteration.
    "_disable_execution_plan_api": True,
    # === Model ===
    # Number of atoms for representing the distribution of return. When
    # this is greater than 1, distributional Q-learning is used.
    # the discrete supports are bounded by v_min and v_max
    "num_atoms": 1,
    "v_min": -10.0,
    "v_max": 10.0,
    # Whether to use noisy network
    "noisy": False,
    # control the initial value of noisy nets
    "sigma0": 0.5,
    # Whether to use dueling dqn
    "dueling": True,
    # Dense-layer setup for each the advantage branch and the value branch
    # in a dueling architecture.
    "hiddens": [256],
    # Whether to use double dqn
    "double_q": True,
    # N-step Q learning
    "n_step": 1,

    # === Replay buffer ===
    # Deprecated, use capacity in replay_buffer_config instead.
    "buffer_size": DEPRECATED_VALUE,
    "replay_buffer_config": {
        # Enable the new ReplayBuffer API.
        "_enable_replay_buffer_api": True,
        "type": "MultiAgentPrioritizedReplayBuffer",
        # Size of the replay buffer. Note that if async_updates is set,
        # then each worker will have a replay buffer of this size.
        # "capacity": 50000,
        "capacity": replay_buffer_config_capacity,
        "replay_batch_size": replay_buffer_config_batch,
        "prioritized_replay_alpha": 0.6,
        # Beta parameter for sampling from prioritized replay buffer.
        "prioritized_replay_beta": 0.4,
        # Epsilon to add to the TD errors when updating priorities.
        "prioritized_replay_eps": 1e-6,
        # The number of continuous environment steps to replay at once. This may
        # be set to greater than 1 to support recurrent models.
        "replay_sequence_length": 1,
    },
    # Set this to True, if you want the contents of your buffer(s) to be
    # stored in any saved checkpoints as well.
    # Warnings will be created if:
    # - This is True AND restoring from a checkpoint that contains no buffer
    #   data.
    # - This is False AND restoring from a checkpoint that does contain
    #   buffer data.
    "store_buffer_in_checkpoints": False,


    # Callback to run before learning on a multi-agent batch of
    # experiences.
    "before_learn_on_batch": None,

    # The intensity with which to update the model (vs collecting samples
    # from the env). If None, uses the "natural" value of:
    # `train_batch_size` / (`rollout_fragment_length` x `num_workers` x
    # `num_envs_per_worker`).
    # If provided, will make sure that the ratio between ts inserted into
    # and sampled from the buffer matches the given value.
    # Example:
    #   training_intensity=1000.0
    #   train_batch_size=250 rollout_fragment_length=1
    #   num_workers=1 (or 0) num_envs_per_worker=1
    #   -> natural value = 250 / 1 = 250.0
    #   -> will make sure that replay+train op will be executed 4x as
    #      often as rollout+insert op (4 * 250 = 1000).
    # See: rllib/agents/dqn/dqn.py::calculate_rr_weights for further
    # details.
    "training_intensity": None,

    # === Parallelism ===
    # Whether to compute priorities on workers.
    "worker_side_prioritization": False,

    # Experimental flag.
    # If True, the execution plan API will not be used. Instead,
    # a Trainer's `training_iteration` method will be called as-is each
    # training iteration.
    "_disable_execution_plan_api": True,
}


