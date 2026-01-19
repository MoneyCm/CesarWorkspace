```javascript
let currentMode = 'calc'; // calc or graph
            margin: { t: 20, b: 20, l: 20, r: 20 },
            paper_bgcolor: '#fff',
            plot_bgcolor: '#fff',
            font: { color: '#000', family: 'Roboto' },
            xaxis: { gridcolor: '#eee' },
            yaxis: { gridcolor: '#eee' }
        };

        if (is3D) {
            let zValues = [];
            for (let i = 0; i < xValues.length; i++) {
                let row = [];
                for (let j = 0; j < yValues.length; j++) {
                    let scope = { x: xValues[i], y: yValues[j] };
                    row.push(expr.evaluate(scope));
                }
                zValues.push(row);
            }
            
            data = [{
                x: xValues,
                y: yValues,
                z: zValues,
                type: 'surface',
                colorscale: 'Viridis',
                showscale: false
            }];
        } else {
            const yPlot = xValues.map(x => {
                return expr.evaluate({ x: x });
            });
            
            data = [{
                x: xValues,
                y: yPlot,
                type: 'scatter',
                mode: 'lines',
                line: { color: '#0077be', width: 2 }
            }];
        }

        Plotly.newPlot(plotDiv, data, layout, { displayModeBar: false, responsive: true });
        
    } catch (err) {
        console.error(err);
        alert("Error al graficar: " + err.message);
    }
}

// Keyboard support
document.addEventListener('keydown', (e) => {
    // Allow default behavior for input field if focused
    if (document.activeElement === screen) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission if any
            calculate();
        }
        return;
    }

    if (e.key >= '0' && e.key <= '9') {
        appendNumber(e.key);
    } else if (e.key === '.') {
        appendNumber('.');
    } else if (e.key === '=' || e.key === 'Enter') {
        calculate();
    } else if (e.key === 'Backspace') {
        deleteLast();
    } else if (e.key === 'Escape') {
        clearScreen();
    } else if (['+', '-', '*', '/', '^', '(', ')'].includes(e.key)) {
        appendOperator(e.key);
    }
});
```
