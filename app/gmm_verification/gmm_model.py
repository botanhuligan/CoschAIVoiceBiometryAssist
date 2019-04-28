import enum
from typing import Optional

import numpy as np
import os

import yaml
from sklearn import preprocessing
import python_speech_features as mfcc
import scipy.io.wavfile as wav
from sklearn.mixture import GaussianMixture
import pickle

path = os.path.dirname(os.path.abspath(__file__))


class VerificationStatus(enum.Enum):
    SUCC = 1,
    FAIL = 2,


def calculate_delta(array):
    """Calculate and returns the delta of given feature vector matrix"""
    rows, cols = array.shape
    deltas = np.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i - j < 0:
                first = 0
            else:
                first = i - j
            if i + j > rows - 1:
                second = rows - 1
            else:
                second = i + j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]] - array[index[0][1]] + (2 * (array[index[1][0]] - array[index[1][1]]))) / 10
    return deltas


def extract_features(audio, rate):
    """extract 20 dim mfcc features from an voice_storage, performs CMS and combines
    delta to make it 40 dim feature vector"""

    mfcc_feat = mfcc.mfcc(audio, rate, 0.025, 0.01, 20, appendEnergy=True)

    mfcc_feat = preprocessing.scale(mfcc_feat)
    delta = calculate_delta(mfcc_feat)
    combined = np.hstack((mfcc_feat, delta))
    return np.array(combined)


def add_user_gmm(user_name: str, *filenames: str):
    assert len(filenames) > 0
    data = None
    for name in filenames:
        fs, signal = wav.read(name)
        if data is None:
            data = extract_features(signal, 1600)
        else:
            data = np.vstack([data, extract_features(signal, 1600)])
    model = GaussianMixture(n_components=16, covariance_type='diag', n_init=3, max_iter=200)
    model.fit(data)
    pickle.dump(model, open(path + "/models/%s.pickle" % user_name, "wb"))


def identify_user(file: str) -> Optional[str]:
    """
    Возвращает ID
    :param file:
    :return:
    """
    fs, signal = wav.read(file)
    features = extract_features(signal, 1600)
    models = os.listdir("models")
    scores = {}
    for model_name in models:
        try:
            user_name, _ = model_name.split(".")
            model = pickle.load(open("models/" + model_name, "rb"))
            scores[user_name] = model.score(features)
        except FileNotFoundError:
            print("No file found")
    if len(scores) == 0:
        return None
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[0][0]


def verify_user(user_name: str, file: str) -> VerificationStatus:
    if user_name == identify_user(file):
        return VerificationStatus.SUCC
    return VerificationStatus.FAIL


def add_voice_snapshot(user_name: str, *files: str):
    assert len(files) > 0
    add_user_gmm(user_name, *files)

