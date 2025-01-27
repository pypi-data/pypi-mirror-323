from hashtron.classifier.constructor import Hashtron
from hashtron.layer.layer import Layer
from hashtron.hash.hash import Hash
from hashtron.net.single_value import SingleValue
from hashtron.net.input import Input

class FeedforwardNetwork:
    def __init__(self, net):
        self.net = net
        self.layers = []
        self.mapping = []
        self.combiners = []
        self.premodulo = []

    def new_layer(self, n: int, bits: int, premodulo: int = 0) -> None:
        layer = [Hashtron.new(None, bits) for _ in range(n)]
        self.layers.append(layer)
        self.mapping.append(bits)
        self.combiners.append(None)
        self.premodulo.append(premodulo)

    def new_combiner(self, layer: Layer) -> None:
        self.layers.append([])
        self.mapping.append(0)
        self.combiners.append(layer)
        self.premodulo.append(0)


    def len_layers(self) -> int:
        """
        Get the number of layers in the network.

        :return: The number of layers.
        """
        return len(self.layers)

    def infer(self, in_val) -> int:
        """
        Infer the network output based on input.

        :param in_val: The input to the network.
        :return: The output of the network.
        """
        if (not hasattr(in_val, 'feature') or not callable(in_val.feature)) and in_val is not Input and in_val is not SingleValue:
            in_val = SingleValue(in_val)
        if (not hasattr(in_val, 'parity') or not callable(in_val.parity)) and in_val is not Input:
            in_val = Input(in_val)
        output = in_val
        for l_prev in range(0, self.len_layers(), 2):
            output, _ = self.forward(output, l_prev, -1, 0)
        val = 0
        for j in range(16):
            if j >= self.get_last_cells():
                break
            val |= (output.feature(j) << j)

        return val ^ in_val.parity()

    def forward(self, in_val, l: int, worst: int, neg: int) -> (Input, bool):
        """
        Forward pass through the network.

        :param in_val: The input to the layer.
        :param l: The layer index.
        :param worst: The index of the worst hashtron.
        :param neg: Whether to negate the worst hashtron's output.
        :return: The intermediate output and a boolean indicating if the worst hashtron's output was computed.
        """
        if len(self.combiners) > l + 1 and self.combiners[l + 1] is not None:
            combiner = self.combiners[l + 1].lay()
            computed = False

            for i in range(len(self.layers[l])):
                feat = in_val.feature(i)
                if self.premodulo[l] != 0:
                    feat = Hash.hash(feat, i, self.premodulo[l])
                bit = self.layers[l][i].forward.forward(feat, (i == worst) and (neg == 1))
                combiner.put(i, (bit & 1) != 0)
                if i == worst:
                    computed = (bit & 1) != 0

            return combiner, computed
        elif len(self.mapping) > l and self.mapping[l] > 0:
            if self.premodulo[l] != 0:
                in_val = SingleValue(Hash.hash(in_val.feature(0), 0, self.premodulo[l]))
            val = self.layers[l][0].forward.forward(in_val.feature(0), (0 == worst) and (neg == 1))
            return SingleValue(val), False
        else:
            if self.premodulo[l] != 0:
                in_val = SingleValue(Hash.hash(in_val.feature(0), 0, self.premodulo[l]))
            bit = self.layers[l][0].forward.forward(in_val.feature(0), (0 == worst) and (neg == 1))
            return SingleValue(bit & 1), (bit & 1) != 0

    def get_bits(self) -> int:
        if len(self.mapping) == 0:
            return 1
        ret = self.mapping[len(self.mapping)-1]
        if ret == 0:
            return 1
        return ret
    
    def get_classes(self) -> int:
        ret = 1 << self.get_bits()
        ret2 = 1 << self.get_last_cells()
        return max(ret, ret2)

    def get_last_cells(self) -> int:
        """
        Get the number of cells in the last non-empty layer of the feedforward network.

        Returns:
            int: Number of cells in the last layer or the second-to-last layer if the last is empty.
        """
        if not self.layers:
            return 0
        
        # Get the number of cells in the last layer
        last_layer_size = len(self.layers[-1])
        
        # If the last layer is empty and there are at least two layers, fall back to the second-to-last layer
        if last_layer_size == 0 and len(self.layers) >= 2:
            last_layer_size = len(self.layers[-2])
        
        return last_layer_size
