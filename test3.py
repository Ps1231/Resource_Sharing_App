
import pdb


class CDF:
    def __init__(self, frequencies, values):
        self.values = values
        self.frequencies = frequencies
        self.prob = self.calculate_prob()
        self.cumulative_prob = self.calculate_cumulative_prob()

    def calculate_prob(self):
        total_frequency = sum(self.frequencies)
        probabilities = [freq / total_frequency for freq in self.frequencies]

        return probabilities

    def calculate_cumulative_prob(self):
        cumulative_prob = [self.prob[0]]
        for i in range(1, len(self.prob)):
            cumulative_prob.append(
                cumulative_prob[i - 1] + self.prob[i])

        return cumulative_prob

    def get_cdf_value(self, x):
        if x < self.values[0]:
            return 0.0
        elif x >= self.values[-1]:
            return 1.0

        for i in range(len(self.values)):
            if x <= self.values[i]:
                return self.cumulative_prob[i]

    def print_cdf(self):
        for i in range(len(self.values)):
            print(
                f'P(X <= {self.values[i]}) = {self.cumulative_prob[i]}')


frequencies = [1, 2, 3, 4]
values = [1, 2, 3, 4]
discrete_distribution = CDF(frequencies, values)
print("Values:", values)
print("Frequencies:", frequencies)
print(" Probabilities: ", discrete_distribution.calculate_prob())
print("cumulative Probabilities: ",
      discrete_distribution.calculate_cumulative_prob())
discrete_distribution.print_cdf()
x_value = 3
cdf_value = discrete_distribution.get_cdf_value(x_value)

print(f'Cumulative Probability for X <= {x_value}: {cdf_value}')