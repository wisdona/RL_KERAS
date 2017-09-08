from model_kkc import Model
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import time
from drawnow import drawnow

def monitorTrainCost(pltSave=False):
    for cost, color, label in zip(mon_cost_list, mon_color_list[0:len(mon_label_list)], mon_label_list):
        plt.plot(mon_epoch_list, cost, c=color, lw=2, ls="--", marker="o", label=label)
    plt.title('Cost Graph per Epoch')
    plt.legend(loc=1)
    plt.xlabel('Epoch')
    plt.ylabel('Cost')
    plt.grid(True)
    if pltSave:
        plt.savefig('Cost Graph per Epoch')

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
    with open(__DATA_PATH + "cat_dog_flower_mushroom_elephant_rhino_data", "r", encoding="utf-8") as file:
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

    label_list = []
    for label in label.tolist():
        if label == 0:
            label_list.append([1,0,0,0,0,0])
        elif label == 1:
            label_list.append([0,1,0,0,0,0])
        elif label == 2:
            label_list.append([0,0,1,0,0,0])
        elif label ==3:
            label_list.append([0,0,0,1,0,0])
        elif label ==4:
            label_list.append([0,0,0,0,1,0])
        else:
            label_list.append([0,0,0,0,0,1])

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
            label_list.append([1,0,0,0,0,0])
        elif label == 1:
            label_list.append([0,1,0,0,0,0])
        elif label == 2:
            label_list.append([0,0,1,0,0,0])
        elif label ==3:
            label_list.append([0,0,0,1,0,0])
        elif label ==4:
            label_list.append([0,0,0,0,1,0])
        else:
            label_list.append([0,0,0,0,0,1])

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

def shuffleLines(lines):
    lines = random.sample(lines, len(lines))
    return random.sample(lines, len(lines))

# early stopping하기 위해 테스트 하는 것을 별도 함수로 구현
def validateModel(MODEL_ACCURACY):

    START_BATCH_INDEX = 0
    ENSEMBLE_ACCURACY = 0
    TEST_ACCURACY_LIST = []
    CNT = 0

    with tf.Session() as sess:

        print('Test Start!')
        models = []
        for m in range(NUM_MODELS):
            models.append(Model(sess, "model" + str(m)))

        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess, 'log/epoch_' + str(LAST_EPOCH) + '.ckpt')

        for epoch in range(TEST_EPHOCHS):

            # 총 데이터의 갯수가 배치사이즈로 나누어지지 않을 경우 버림한다
            total_batch_num = math.trunc(len(TEST_DATA) / BATCH_SIZE)

            for i in range(total_batch_num):

                print("Test Batch Data Reading {}/{}".format(i + 1, total_batch_num))

                # test_x_batch, test_y_batch = loadMiniBatch(TEST_DATA)
                test_x_batch, test_y_batch = loadBatch(TEST_DATA, START_BATCH_INDEX)

                test_size = len(test_y_batch) # 테스트 데이터
                predictions = np.zeros(test_size * CLASS_NUM).reshape(test_size, CLASS_NUM) # [[0.0, 0.0], [0.0, 0.0] ...]
                model_result = np.zeros(test_size * CLASS_NUM, dtype=np.int).reshape(test_size, CLASS_NUM)  #[ [0,0], [0,0]...]
                model_result[:, 0] = range(0, test_size) # [[0,0],[1,0], [2,0], [3,0] ......]

                for idx, m in enumerate(models):
                    MODEL_ACCURACY[idx] += m.get_accuracy(test_x_batch, test_y_batch) # 모델의 정확도가 각 인덱스에 들어감 [0.92, 0.82, 0.91]
                    p = m.predict(test_x_batch) # 모델이 분류한 라벨 값
                    model_result[:, 1] = np.argmax(p, 1) #  두번째 인덱스에 p중 가장 큰값을 넣는다 [[0,0],[1,1], [2,1], [3,0] ......]
                    for result in model_result:
                        predictions[result[0], result[1]] += 1

                ensemble_correct_prediction = tf.equal(tf.argmax(predictions, 1), tf.argmax(test_y_batch, 1))
                ENSEMBLE_ACCURACY += tf.reduce_mean(tf.cast(ensemble_correct_prediction, tf.float32))
                TEST_ACCURACY_LIST.append(ENSEMBLE_ACCURACY)
                CNT += 1

            START_BATCH_INDEX = 0

            for i in range(len(MODEL_ACCURACY)):
                print('Model ' + str(i) + ' : ', MODEL_ACCURACY[i] / CNT)
            print('Ensemble Accuracy : ', sess.run(ENSEMBLE_ACCURACY) / CNT)
            print('Testing Finished!')
        print("TEST_EPHOCH 수: {}, 최대 정확도: {}".format(TEST_EPHOCHS,np.max(TEST_ACCURACY_LIST, axis=-1)))

def predictConsumtionTime():
    """
    총소요시간 = 배치 사이즈 * a * 앙상블 모델의 수 * 배치 횟수(per Epoch) * 전체 Ephoc 수
    0.0053 : 이미지 1개당 연산 시간(현재모델 0.0053)
    alpha = 총소요시간 / (배치사이즈 * 앙상블 모델의 수 * 배치 횟수 * 전체 Ephoc 수)
    alpha 를 구하기 위해서는 전체 소요시간을 1회 측정해서 구해야한다.
    """
    alpha = 0.0053
    c_time = BATCH_SIZE * 0.0053 * NUM_MODELS * math.trunc(int(len(TRAIN_DATA)/BATCH_SIZE)) * TRAIN_EPOCHS
    print("모델 학습 예상 소요시간: {} 분".format(float(c_time/60)))
    pass


# 학습을 위한 기본적인 셋팅
__DATA_PATH = "preprocessed_data/"
IMG_SIZE = (144, 144)
BATCH_SIZE = 100
START_BATCH_INDEX = 0
TRAIN_EPOCHS = 8
TEST_EPHOCHS = 2
TRAIN_RATE = 0.8
NUM_MODELS = 3
CLASS_NUM = 6

# Random Mini Batch의 데이터 중복 허용 여부를 정한다. 순서(Order)가 True 경우 중복이 허용되지 않는다.
# 둘다 False 일 경우 : Random mini batch no order(데이터 중복허용)을 수행

RANDOM_MINI_BATCH_NO_ORDER = False
MIN_ORDER_BATCH_EPCHO = 0 # Random mini batch 시 Normal Batch를 몇 회 수행 후 미니배치를 수행할 것인지 정하는 변수

RANDOM_MINI_BATCH_ORDER = False # 중복없는 랜덤 미니배치
NORMAL_BATCH = True # 일반배치

MODEL_ACCURACY = np.zeros(NUM_MODELS).tolist()
LAST_EPOCH = None

# monitoring 관련 parameter
mon_epoch_list = []
mon_cost_list = [[] for m in range(NUM_MODELS)]
mon_color_list = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
mon_label_list = ['model'+str(m+1) for m in range(NUM_MODELS)]

# TRAIN_DATA와 TEST_DATA를 셋팅, 실제 각 변수에는 txt파일의 각 line 별 주소 값이 리스트로 담긴다.
stime = time.time()
TRAIN_DATA, TEST_DATA = loadInputData()
# 종료 시간 체크
etime = time.time()
print('Data Loading Consumption Time : ', round(etime - stime, 6))
predictConsumtionTime()

# TRAIN
with tf.Session() as sess:
    # 시작 시간 체크
    stime = time.time()
    models = []
    # initialize
    for m in range(NUM_MODELS):
        models.append(Model(sess, "model" + str(m)))

    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()

    print('Learning Started!')

    # train my model
    for epoch in range(TRAIN_EPOCHS):

        avg_cost_list = np.zeros(len(models))

        # 총 데이터의 갯수가 배치사이즈로 나누어지지 않을 경우 버림한다
        total_batch_num = math.trunc(int(len(TRAIN_DATA) / BATCH_SIZE))

        ################################################################################
        ###  - 랜덤 미니배치(데이터 중복 또는 중복 불가) 또는 일반배치를 설정하는 부분
        ###  - RANDOM_MINI_BATCH_ORDER의 Boolen 값에 따라 수행하는 것이 달라진다.
        ################################################################################

        # 랜덤 미니배치 중복없이 할 경우 매 에폭마다 Train Data를 섞어준다.
        if RANDOM_MINI_BATCH_ORDER:
            print("랜덤 미니배치(중복불가)를 수행합니다. Data Shuffle")
            TRAIN_DATA = shuffleLines(TRAIN_DATA)
        elif NORMAL_BATCH:
            print("일반 배치(중복불가)를 수행합니다.")
        else:
            print("랜덤 미니배치(중복허용)를 수행합니다.")

        for i in range(total_batch_num):

            # MINI_BATCH 여부에 따라 나뉜다.
            # 중복 없는 Random Mini Batch
            if RANDOM_MINI_BATCH_ORDER:
                print("[데이터 중복 불가] {} Epoch: Random Mini Batch Data Reading {}/{}".
                      format(epoch + 1, i + 1, total_batch_num))
                train_x_batch, train_y_batch = loadBatch(TRAIN_DATA, START_BATCH_INDEX)

            # Normal Batch
            elif NORMAL_BATCH:
                print("[데이터 중복 불가] {} Epoch: Normal Batch Data Reading {}/{}".
                      format(epoch + 1, i + 1, total_batch_num))
                train_x_batch, train_y_batch = loadBatch(TRAIN_DATA, START_BATCH_INDEX)

            # 중복 허용 Random Mini Batch
            elif RANDOM_MINI_BATCH_NO_ORDER:

                # 특정 Epoch만큼 데이터 중복없이 일반배치 또는 랜덤미니배치를 수행을 설정하는 부분
                if epoch < MIN_ORDER_BATCH_EPCHO:
                    print("[데이터 중복 불가] {}/{} Epoch : Normal Batch Data Reading {}/{}".
                          format(epoch + 1, MIN_ORDER_BATCH_EPCHO, i + 1, total_batch_num))
                    train_x_batch, train_y_batch = loadBatch(TRAIN_DATA,START_BATCH_INDEX)
                else:
                    print("[데이터 중복 허용] {} Epoch: Random Mini Batch Data Reading {}/{}".
                          format(epoch + 1, i + 1, total_batch_num))
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

    drawnow(monitorTrainCost, pltSave=True)
    print('Learning Finished!')
    saver.save(sess, 'log/epoch_' + str(LAST_EPOCH) + '.ckpt')

    # 종료 시간 체크
    etime = time.time()
    print('Consumption Time : ', round(etime - stime, 6))


tf.reset_default_graph()
validateModel(MODEL_ACCURACY)



