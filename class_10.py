from resnet_no_bottle_34layer import Model
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import time
from scipy import ndimage
from drawnow import drawnow
from pandas_ml import ConfusionMatrix


def monitorTrainCost(pltSave=False):
    for cost, color, label in zip(mon_cost_list, mon_color_list[0:len(mon_label_list)], mon_label_list):
        plt.plot(mon_epoch_list, cost, c=color, lw=2, ls="--", marker="o", label=label)
    plt.title('Cost Graph per Epoch')
    plt.legend(loc=1)
    plt.xlabel('Epoch')
    plt.ylabel('Cost')
    plt.grid(True)
    if pltSave:
        plt.savefig('Cost Graph per Epoch {}_{}'.format(CLASS_NUM,time.asctime()))

def plotImage(image):
    """image array를 plot으로 보여주는 함수
    Args:
        image (2-D or 3-D array): (H, W) or (H, W, C)
    """
    image = np.squeeze(image)
    shape = image.shape

    if len(shape) == 2:
        plt.imshow(image, cmap="gray")
    else:
        plt.imshow(image)
    plt.show()

def loadInputData():
    """
    텍스트화된 이미지 txt파일을 로드하는 함수
    :return: TRAIN_DATA, TEST_DATA
    """
    print("Loading Data")
    with open(__DATA_PATH + "128_cat_dog_flower_mushroom_elephant_rhino_nature_building_simson_snake_data", "r", encoding="utf-8") as file:
        # lines : 모든 lines(데이터행)을 불러온다.
        lines = file.readlines()

        # 불러온 전체 lines를 셔플한다.
        lines = random.sample(lines, len(lines))
        lines = random.sample(lines, len(lines))
        lines = random.sample(lines, len(lines))

        # train data를 일정 rate 만큼 뽑아오기 위한 단계
        train_last_index = round(TRAIN_RATE * len(lines))
        file.close()
        # return 시 데이터를 섞어서 return 한다.
        return lines[:train_last_index], lines[train_last_index:]

def loadRandomMiniBatch(lines):
    """
    랜덤 미니배치함수
    txt파일에서 불러온 lines를 읽어서 input data인 numpy array로 바꾸기 위한 함수
    :param lines: loadInputData함수를 통해 불러온 .txt파일의 lines
    :return: numpy arrary의 input data로 X, Y(라벨)을 각각 나누어 리턴한다.
    """
    lines = random.sample(lines, BATCH_SIZE)
    # 각 line은 string으로 되어 있으므로 split한다. split된 리스트 마지막에 '\n'이 추가되므로 [:-1]로 제거한다.
    data = [line.split(',')[:-1] for line in lines]
    data = np.array(data, dtype=np.float32)

    # X,Y를 나누는 작업
    data, label = data[:, :-1], data[:, -1]
    data = data / 255.

    # 라벨을 one_hot으로 바꾼다.
    # label = [[1, 0] if label == 0 else [0, 1] for label in label.tolist()]
    if IMAGE_DISTORT_RATE > random.random():
        data = distortImage(data)

    label_list = []
    for label in label.tolist():
        if label == 0:
            label_list.append([1,0,0,0,0,0,0,0,0,0])
        elif label == 1:
            label_list.append([0,1,0,0,0,0,0,0,0,0])
        elif label == 2:
            label_list.append([0,0,1,0,0,0,0,0,0,0])
        elif label == 3:
            label_list.append([0,0,0,1,0,0,0,0,0,0])
        elif label == 4:
            label_list.append([0,0,0,0,1,0,0,0,0,0])
        elif label == 5:
            label_list.append([0,0,0,0,0,1,0,0,0,0])
        elif label == 6:
            label_list.append([0,0,0,0,0,0,1,0,0,0])
        elif label == 7:
            label_list.append([0,0,0,0,0,0,0,1,0,0])
        elif label == 8:
            label_list.append([0,0,0,0,0,0,0,0,1,0])
        elif label == 9:
            label_list.append([0,0,0,0,0,0,0,0,0,1])

    # label_list = []
    # for label in label.tolist():
    #     if label == 0:
    #         label_list.append([1,0,0,0])
    #     elif label == 1:
    #         label_list.append([0,1,0,0])
    #     elif label == 2:
    #         label_list.append([0,0,1,0])
    #     elif label ==3:
    #         label_list.append([0,0,0,1])



    label = np.array(label_list)
    return data, label

def loadBatch(lines, START_BATCH_INDEX):
    """
    일반 배치함수
    :param lines: loadInputData함수를 통해 불러온 .txt파일의 lines
    :param START_BATCH_INDEX: 데이터를 차례로 가져오기 위한 index 값
    :return: numpy arrary의 input data로 X, Y(라벨)을 각각 나누어 리턴한다.
    """
    # 각 line은 string으로 되어 있으므로 split한다. split된 리스트 마지막에 '\n'이 추가되므로 [:-1]로 제거한다.
    lines = lines[START_BATCH_INDEX:START_BATCH_INDEX+BATCH_SIZE]
    START_BATCH_INDEX += BATCH_SIZE
    data = [line.split(',')[:-1] for line in lines]
    data = np.array(data, dtype=np.float32)

    # X,Y를 나누는 작업
    data, label = data[:, :-1], data[:, -1]
    data = data / 255.

    # 고양이, 개 사진이 잘 섞였는지 확인하는 부분
    # for idx, l in enumerate(label):
    #     if l == 0:
    #         print(l)
    #         print("고양이입니다.")
    #     else:
    #         print(l)
    #         print("개입니다.")
    #     plotImage(data[idx].reshape(144,144))

    # 라벨을 one_hot으로 바꾼다.
    # label = [[1, 0] if label == 0 else [0, 1] for label in label.tolist()]

    label_list = []
    for label in label.tolist():
        if label == 0:
            label_list.append([1,0,0,0,0,0,0,0,0,0])
        elif label == 1:
            label_list.append([0,1,0,0,0,0,0,0,0,0])
        elif label == 2:
            label_list.append([0,0,1,0,0,0,0,0,0,0])
        elif label == 3:
            label_list.append([0,0,0,1,0,0,0,0,0,0])
        elif label == 4:
            label_list.append([0,0,0,0,1,0,0,0,0,0])
        elif label == 5:
            label_list.append([0,0,0,0,0,1,0,0,0,0])
        elif label == 6:
            label_list.append([0,0,0,0,0,0,1,0,0,0])
        elif label == 7:
            label_list.append([0,0,0,0,0,0,0,1,0,0])
        elif label == 8:
            label_list.append([0,0,0,0,0,0,0,0,1,0])
        elif label == 9:
            label_list.append([0,0,0,0,0,0,0,0,0,1])



    label = np.array(label_list)
    return data, label, START_BATCH_INDEX

def loadAllTestLabel(lines):
    labels = [line.split(',')[-2] for line in lines]
    labels = np.array(labels, dtype=np.uint8)
    label_list = []

    for label in labels:
        if label == 0:
            label_list.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        elif label == 1:
            label_list.append([0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        elif label == 2:
            label_list.append([0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
        elif label == 3:
            label_list.append([0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
        elif label == 4:
            label_list.append([0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        elif label == 5:
            label_list.append([0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
        elif label == 6:
            label_list.append([0, 0, 0, 0, 0, 0, 1, 0, 0, 0])
        elif label == 7:
            label_list.append([0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
        elif label == 8:
            label_list.append([0, 0, 0, 0, 0, 0, 0, 0, 1, 0])
        elif label == 9:
            label_list.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])

    label = np.array(label_list)
    return label

def onehot2label(label_array):

    label_list = np.argmax(label_array, axis=1)
    return label_list.tolist()

def shuffleLines(lines):
    lines = random.sample(lines, len(lines))
    return random.sample(lines, len(lines))

def predictConsumtionTime(epoch_num):
    """
    총소요시간 = 배치 사이즈 * a * 앙상블 모델의 수 * 배치 횟수(per Epoch) * 전체 Ephoc 수
    0.0053 : 이미지 1개당 연산 시간(현재모델 0.0053)
    alpha = 총소요시간 / (배치사이즈 * 앙상블 모델의 수 * 배치 횟수 * 전체 Ephoc 수)
    alpha 를 구하기 위해서는 전체 소요시간을 1회 측정해서 구해야한다.
    """
    alpha = 0.0053
    c_time = BATCH_SIZE * 0.0053 * NUM_MODELS * math.trunc(int(len(TRAIN_DATA)/BATCH_SIZE)) * epoch_num
    c_time = float(c_time/60)
    print("총 {} 에폭 학습, 학습 예상 소요시간: {} 분".format(epoch_num,c_time))
    return c_time

def distortImage(images):
    return ndimage.uniform_filter(images, size=11)

# 학습을 위한 기본적인 셋팅
__DATA_PATH = "preprocessed_data/"
IMG_SIZE = (144, 144)
BATCH_SIZE = 100
START_BATCH_INDEX = 0
#
# 학습 도중 이미지를 Distort하는 데이터의 비중
IMAGE_DISTORT_RATE = 0

# EARLY_STOP 시작하는 에폭 시점
START_EARLY_STOP_EPOCH = 5
START_EARLY_STOP_COST = 0.01

TRAIN_RATE = 0.8
NUM_MODELS = 1
CLASS_NUM = 10
TEST_ACCURACY_LIST = []
START_BATCH_INDEX = 0


# Random Mini Batch의 데이터 중복 허용 여부를 정한다. 순서(Order)가 True 경우 중복이 허용되지 않는다.
# 둘다 False 일 경우 : Random mini batch no order(데이터 중복허용)을 수행

RANDOM_MINI_BATCH_NO_ORDER = False
MIN_ORDER_BATCH_EPCHO = 0 # Random mini batch 시 Normal Batch를 몇 회 수행 후 미니배치를 수행할 것인지 정하는 변수

RANDOM_MINI_BATCH_ORDER = True # 중복없는 랜덤 미니배치
NORMAL_BATCH = False # 일반배치


LAST_EPOCH = None

# monitoring 관련 parameter
mon_epoch_list = []
mon_cost_list = [[] for m in range(NUM_MODELS)]
mon_color_list = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
mon_label_list = ['model'+str(m+1) for m in range(NUM_MODELS)]

# TRAIN_DATA와 TEST_DATA를 셋팅, 실제 각 변수에는 txt파일의 각 line 별 주소 값이 리스트로 담긴다.
stime = time.time()
TRAIN_DATA, TEST_DATA = loadInputData()
#loadAllTestLabel(TEST_DATA)

print("Train Data {}개 , Test Data {}개 ".format(len(TRAIN_DATA), len(TEST_DATA)))

# for line in TRAIN_DATA:
#     line = line.split(',')
#     line.pop()
#     line.pop()
#     line = np.array(line, dtype=np.float32).reshape(144,144)
#     line = line/255.
#     plotImage(line)

# 종료 시간 체크
etime = time.time()
print('Data Loading Consumption Time : ', round(etime - stime, 6))
predictConsumtionTime(START_EARLY_STOP_EPOCH)

# TRAIN
with tf.Session() as sess:
    # 시작 시간 체크
    stime = time.time()
    models = []
    valid_result = []
    epoch = 0
    # initialize
    for m in range(NUM_MODELS):
        models.append(Model(sess, "model" + str(m), CLASS_NUM))

    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()

    print('Learning Started!')

    # train my model
    # for epoch in range(TRAIN_EPOCHS):
    while True:
        avg_cost_list = np.zeros(len(models))

        # 총 데이터의 갯수가 배치사이즈로 나누어지지 않을 경우 버림한다
        total_batch_num = math.trunc(int(len(TRAIN_DATA) / BATCH_SIZE))

        ################################################################################
        ###  - 랜덤 미니배치(데이터 중복 또는 중복 불가) 또는 일반배치를 설정하는 부분
        ###  - RANDOM_MINI_BATCH_ORDER의 Boolen 값에 따라 수행하는 것이 달라진다.
        ################################################################################

        # 랜덤 미니배치 중복없이 할 경우 매 에폭마다 Train Data를 섞어준다.
        if RANDOM_MINI_BATCH_ORDER:
            # print("랜덤 미니배치(중복불가)를 수행합니다. Data Shuffle")
            TRAIN_DATA = shuffleLines(TRAIN_DATA)
        # elif NORMAL_BATCH:
        #     print("일반 배치(중복불가)를 수행합니다.")
        # else:
        #     print("랜덤 미니배치(중복허용)를 수행합니다.")

        for i in range(total_batch_num):

            # MINI_BATCH 여부에 따라 나뉜다.
            # 중복 없는 Random Mini Batch
            if RANDOM_MINI_BATCH_ORDER:
                # print("[데이터 중복 불가] {} Epoch: Random Mini Batch Data Reading {}/{}, DATA INDEX : {}".
                #       format(epoch + 1, i + 1, total_batch_num,START_BATCH_INDEX))
                train_x_batch, train_y_batch, START_BATCH_INDEX = loadBatch(TRAIN_DATA, START_BATCH_INDEX)

            # Normal Batch
            elif NORMAL_BATCH:
                # print("[데이터 중복 불가] {} Epoch: Normal Batch Data Reading {}/{}, DATA INDEX : {}".
                #       format(epoch + 1, i + 1, total_batch_num, START_BATCH_INDEX))
                train_x_batch, train_y_batch, START_BATCH_INDEX = loadBatch(TRAIN_DATA, START_BATCH_INDEX)

            # 중복 허용 Random Mini Batch
            elif RANDOM_MINI_BATCH_NO_ORDER:

                # 특정 Epoch만큼 데이터 중복없이 일반배치 또는 랜덤미니배치를 수행을 설정하는 부분
                if epoch < MIN_ORDER_BATCH_EPCHO:
                    # print("[데이터 중복 불가] {}/{} Epoch : Normal Batch Data Reading {}/{}, DATA INDEX : {}".
                    #       format(epoch + 1, MIN_ORDER_BATCH_EPCHO, i + 1, total_batch_num, START_BATCH_INDEX))
                    train_x_batch, train_y_batch, START_BATCH_INDEX = loadBatch(TRAIN_DATA,START_BATCH_INDEX)
                else:
                    # print("[데이터 중복 허용] {} Epoch: Random Mini Batch Data Reading {}/{}".
                    #       format(epoch + 1, i + 1, total_batch_num))
                    train_x_batch, train_y_batch = loadRandomMiniBatch(TRAIN_DATA)

            # Train each model
            for m_idx, m in enumerate(models):
                c, _ = m.train(train_x_batch, train_y_batch)
                avg_cost_list[m_idx] += c / total_batch_num

        print('Epoch:', '%04d' % (epoch + 1), 'cost =', avg_cost_list)
        START_BATCH_INDEX = 0
        LAST_EPOCH = epoch+1

        mon_epoch_list.append(epoch + 1)
        for idx, cost in enumerate(avg_cost_list):
            mon_cost_list[idx].append(cost)
        drawnow(monitorTrainCost)

        epoch += 1

        ###################################################################################
        ## Early Stop, Test 검증
        ################################################################################
        if (epoch >= START_EARLY_STOP_EPOCH) and float(np.mean(avg_cost_list)) < START_EARLY_STOP_COST:
            # Test 수행 시 마다 초기화가 필요한 변수들
            MODEL_ACCURACY = np.zeros(NUM_MODELS).tolist()
            CNT = 0
            TEST_ACCURACY = None
            ENSEMBLE_ACCURACY = 0
            TEST_DATA = shuffleLines(TEST_DATA)
            test_total_batch_num = math.trunc(len(TEST_DATA) / BATCH_SIZE)
            ALL_TEST_LABELS = []
            predictions = np.zeros(test_total_batch_num * BATCH_SIZE * CLASS_NUM)\
                .reshape(-1,CLASS_NUM)  # [[0.0, 0.0], [0.0, 0.0] ...]

            print("{} Epoch 모델에 대한 검증을 시작합니다.".format(epoch))
            # 모델 검증
            # 총 데이터의 갯수가 배치사이즈로 나누어지지 않을 경우 버림한다

            for i in range(test_total_batch_num):

                # print("Test Batch Data Reading {}/{}, DATA INDEX : {}".format(i + 1, test_total_batch_num, START_BATCH_INDEX))

                # test_x_batch, test_y_batch = loadMiniBatch(TEST_DATA)
                test_x_batch, test_y_batch, START_BATCH_INDEX = loadBatch(TEST_DATA, START_BATCH_INDEX) # 리턴 시 START_BATCH_INDEX는 + BATCH_SZIE 되어 있음
                ALL_TEST_LABELS.append(test_y_batch)

                # 모든 앙상블 모델들에 대해 각각 모델의 정확도와 predict를 구하는 과정
                for idx, m in enumerate(models):
                    MODEL_ACCURACY[idx] += m.get_accuracy(test_x_batch,
                                                          test_y_batch)  # 모델의 정확도가 각 인덱스에 들어감 [0.92, 0.82, 0.91]
                    p = m.predict(test_x_batch)  # 모델이 분류한 라벨 값
                    # 위에서 load배치 함수를 호출하면 START_BATCH_INDEX가 BATCH_SIZE만큼 증가하기 때문에 다시 빼준다.
                    predictions[START_BATCH_INDEX-BATCH_SIZE:START_BATCH_INDEX,:] += p

                CNT += 1
            ALL_TEST_LABELS = np.array(ALL_TEST_LABELS).reshape(-1,CLASS_NUM)
            ensemble_correct_prediction = tf.equal(tf.argmax(predictions, 1), tf.argmax(ALL_TEST_LABELS, 1))
            ENSEMBLE_ACCURACY += tf.reduce_mean(tf.cast(ensemble_correct_prediction, tf.float32))

            START_BATCH_INDEX = 0

            for i in range(len(MODEL_ACCURACY)):
                print('Model ' + str(i) + ' : ', MODEL_ACCURACY[i] / CNT)
            TEST_ACCURACY = sess.run(ENSEMBLE_ACCURACY)
            print('Ensemble Accuracy : ', TEST_ACCURACY)
            print('Testing Finished!')

            actual_confusionMatrix = onehot2label(ALL_TEST_LABELS)
            prediction_confusionMatrix = onehot2label(predictions)
            confusion_matrix = ConfusionMatrix(actual_confusionMatrix, prediction_confusionMatrix)
            confusion_matrix.print_stats()


            TEST_ACCURACY_LIST.append(TEST_ACCURACY)
            if len(TEST_ACCURACY_LIST) != 1:
                if float(TEST_ACCURACY_LIST[0]) >= float(TEST_ACCURACY_LIST[1]) :
                    print("이전 정확도: {}, 현재 정확도:{} ".format(TEST_ACCURACY_LIST[0], TEST_ACCURACY_LIST[1]))
                    print("Ealry Stop 으로 학습을 중단합니다.")
                    print("최고정확도 {}".format(TEST_ACCURACY_LIST[0]))
                    break
                else:
                    print("이전 정확도: {}, 현재 정확도:{} ".format(TEST_ACCURACY_LIST[0], TEST_ACCURACY_LIST[1]))
                    TEST_ACCURACY_LIST[0] = TEST_ACCURACY_LIST[1]
                    TEST_ACCURACY_LIST.pop()
                    saver.save(sess, 'log/epoch_' + str(LAST_EPOCH) + '.ckpt')
                    print("학습을 계속 진행합니다.")

    drawnow(monitorTrainCost, pltSave=True)
    print('Learning Finished!')

    # 종료 시간 체크
    etime = time.time()
    c_time = round(etime - stime, 6)/60
    p_time = predictConsumtionTime(LAST_EPOCH-1)

    print('Total Consumption Time : {} 분'.format(c_time))
    print('학습에 소요된 Consumption Time : 약 {} 분'.format(p_time))
    print('Early Stoping에 소요된 Consumption Time : 약 {} 분'.format(c_time-p_time))






