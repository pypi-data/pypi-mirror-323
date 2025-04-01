[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![pipeline status](https://git.uni-luebeck.de/its/anomed/deanonymizer/badges/main/pipeline.svg?ignore_skipped=true)
![coverage](https://git.uni-luebeck.de/its/anomed/deanonymizer/badges/main/coverage.svg?job=run_tests)

# Deanonymizer

A library aiding to create attacks against anonymizers (privacy preserving
machine learning models) for the AnoMed competition platform. Currently, only
membership inference attacks are supported.

# Usage Example

The following example will create a Falcon-based web app that encapsulates a
deanonymizer, targeting the example anonymizer defined in the [anomed-anonyimzer](https://pypi.org/project/anomed-anonymizer/)
README.md (which is a privacy preserving classifier for the famous iris dataset
classification problem). The encapsulated deanonymizer is a [membership inference
black box attack](https://adversarial-robustness-toolbox.readthedocs.io/en/latest/modules/attacks/inference/membership_inference.html#membership-inference-black-box),
implemented using the Adversarial Robustness Toolbox ([ART library](https://github.com/Trusted-AI/adversarial-robustness-toolbox)).

The web app offers these routes (some may have query parameters not mentioned here):

    [GET] / (This displays an "alive message".)
    [POST] /fit (This invokes fitting the Gaussian naive based classifier; the web app will pull the training data from training_data_url.)
    [POST] /evaluate (This invokes an intermediate, or final evaluation of the classifier.)

```python
import anomed_deanonymizer
import numpy as np
from art.attacks.inference.membership_inference import MembershipInferenceBlackBox


def validate_input_array(feature_array: np.ndarray) -> None:
    if feature_array.shape[1] != 4 or len(feature_array.shape) != 2:
        raise ValueError("Feature array needs to have shape (n_samples, 4).")
    if feature_array.dtype != np.float_:
        raise ValueError("Feature array must be an array of floats.")


attack_target = anomed_deanonymizer.WebClassifier(
    url="http://example.com/predict", input_shape=(4,), nb_classes=3
)
example_attack_art = MembershipInferenceBlackBox(estimator=attack_target)  # type: ignore
example_attack = anomed_deanonymizer.ARTWrapper(
    art_mia=example_attack_art, input_validator=validate_input_array
)
application = anomed_deanonymizer.supervised_learning_MIA_server_factory(
    anonymizer_identifier="example_anonymizer",
    deanonymizer_identifier="example_deanonymizer",
    deanonymizer_obj=example_attack,
    model_filepath="deanonymizer.pkl",
    default_batch_size=64,
    member_url="http://example.com/members",
    nonmember_url="http://example.com/non-members",
    evaluation_data_url="http://example.com/attack-success-evaluation",
    model_loader=anomed_deanonymizer.unpickle_deanonymizer,
    utility_evaluation_url="http://example.com/utility",
)

```
