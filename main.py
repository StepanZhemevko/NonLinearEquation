import matplotlib
matplotlib.use('Agg')  # Use the Agg backend

from flask import Flask, render_template, request
import sympy
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, template_folder='/home/stepan/PycharmProjects/Cursova/templates')

def generate_graph(function):
    x_values = np.linspace(-10, 10, 100)
    y_values = function(x_values)

    plt.plot(x_values, y_values, label='Function')
    plt.title('Graph of the Function')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Close the figure to release resources
    plt.close()

    return graph_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        equation_str = request.form['equation']
        x = sympy.Symbol('x')

        try:
            equation = sympy.sympify(equation_str)
            initial_str = request.form.get('initial', '1')
            initial = float(initial_str)
            tolerance_str = request.form.get('tolerance', '1e-6')
            tolerance = float(tolerance_str)
            max_iterations_str = request.form.get('max_iterations', '100')
            max_iterations = int(max_iterations_str)
            function = sympy.lambdify(x, equation)
            derivative = sympy.lambdify(x, sympy.diff(equation, x))

            if tolerance <= 0:
                raise ValueError("Tolerance must be positive.")
            if max_iterations <= 0:
                raise ValueError("Max iterations must be positive.")

            iterations = 0
            x_new = initial
            x_old = x_new + 2 * tolerance
            errors = []

            while abs(x_new - x_old) > tolerance and iterations < max_iterations:
                x_old = x_new
                x_new = x_old - function(x_old) / derivative(x_old)
                iterations += 1
                deviation = abs(x_new - x_old)
                errors.append((iterations, deviation))

            if iterations == max_iterations:
                solution = "Did not converge"
            else:
                solution = x_new

            graph_data = generate_graph(function)

            return render_template('index.html', solution=solution, equation=equation_str, initial=initial_str,
                                   tolerance=tolerance_str, max_iterations=max_iterations_str,
                                   num_iterations=iterations, errors=errors, graph_data=graph_data)
        except (sympy.SympifyError, ValueError) as e:
            return render_template('error.html', error_message=str(e))

    else:
        return render_template('index.html')

@app.route('/error')
def error():
    return render_template('error.html', error_message='Invalid request.')

if __name__ == '__main__':
    app.run(debug=True)
