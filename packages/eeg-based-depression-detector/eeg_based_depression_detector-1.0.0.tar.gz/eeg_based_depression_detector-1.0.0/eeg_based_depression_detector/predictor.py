# depression_detector/predictor.py
import pkg_resources
import numpy as np
import networkx as nx
from node2vec import Node2Vec
from gensim.models import Word2Vec
from sklearn.preprocessing import StandardScaler
import joblib
from scipy.io import loadmat



class DepressionDetector:
    def __init__(self):
        # 自动获取模型路径
        model_path = pkg_resources.resource_filename(
            'eeg_based_depression_detector',
            'data/depression_detection_model.pkl'
        )
        components = joblib.load(model_path)
        self.features = components['train_features']  # 原始特征 (53, 128)
        self.original_graph = components['fusion_graph']  # 原始图结构
        self.model = components['node2vec_model']  # Node2Vec模型
        self.classifier = components['knn_classifier']  # KNN分类器
        self.scaler = components['feature_scaler']  # 标准化器
        self.num_channels = components['metadata']['num_channels']

        # 预计算参数
        self.original_embeddings = self.scaler.transform(
            np.array([self.model.wv[str(i)] for i in range(53)])
        )
    def mat2narray(self, filePath):
        """
        输入：matlab脑电矩阵文件地址
        输出：对应的特征向量，长度应为128
        """
        features = []
        data = loadmat(filePath)
        key = [k for k in data.keys() if not k.startswith('__')][0]  # 找到主数据键
        eeg_data = data[key][:-1, :]  # 去掉最后一行
        features = eeg_data.mean(axis=1)  # 计算每个通道的均值作为特征向量
        return np.array(features)

    def predict(self, new_eeg):
        """
        输入: 预处理后的eeg特征向量 (128,)
        输出: 抑郁症概率 (0-1)
        """
        # 1. 构建增量图
        extended_graph = self._extend_graph(new_eeg)

        # 2. 生成新嵌入
        new_embedding = self._generate_embedding(extended_graph)

        # 3. 标准化并预测
        scaled_embedding = self.scaler.transform(new_embedding.reshape(1, -1))
        return self.classifier.predict_proba(scaled_embedding)[0][1]

    def _extend_graph(self, new_sample):
        """构建包含新样本的扩展图"""
        # 复制原始图
        G = self.original_graph.copy()
        new_node_id = 53  # 新节点ID

        # 添加新节点
        G.add_node(new_node_id)

        # 计算通道级相似度权重
        channel_weights = []
        for c in range(self.num_channels):
            # 计算当前通道所有样本的特征
            channel_features = self.features[:, c].reshape(-1, 1)
            new_feature = new_sample[c]

            # 计算归一化距离
            distances = np.abs(channel_features - new_feature)
            normalized = (distances - distances.min()) / (distances.max() - distances.min())
            channel_weights.append(1 - normalized)  # 转换为相似度

        # 融合权重计算
        channel_weights = np.stack(channel_weights).mean(axis=0)

        # 添加新边
        for i in range(53):
            # 计算融合权重（各通道平均）
            avg_weight = channel_weights[i][0]
            G.add_edge(new_node_id, i, weight=avg_weight)

        return G

    def _generate_embedding(self, graph):
        """生成新节点的嵌入向量"""
        # 配置Node2Vec参数（与训练时相同）
        node2vec = Node2Vec(
            graph,
            dimensions=128,
            walk_length=100,
            num_walks=10,
            p=0.5,
            q=2,
            workers=4
        )

        # 只训练新节点的嵌入，固定原有节点
        walks = node2vec.walks  # 生成的随机游走句子（节点ID集合）

        # 将节点序列转换为字符串表示
        walks_str = [[str(node) for node in walk] for walk in walks]

        model = Word2Vec(sentences=walks_str, vector_size=128, window=2, sg=1, workers=4, epochs=10, min_count=1)

        return model.wv['53']  # 返回新节点嵌入


# depression_detector/predictor.py
def main():
    import argparse
    import numpy as np

    parser = argparse.ArgumentParser(description='eeg_based_depression_detector')
    parser.add_argument('-f', '--file', help='Path to eeg .npy file')
    args = parser.parse_args()

    detector = DepressionDetector()

    if args.file:
        data = detector.mat2narray(args.file)
    else:
        print("No input provided, running example...")
        data = np.random.randn(128)

    proba = detector.predict(data)
    print(f"\nDepression Probability: {proba:.2%}")


if __name__ == "__main__":
    main()