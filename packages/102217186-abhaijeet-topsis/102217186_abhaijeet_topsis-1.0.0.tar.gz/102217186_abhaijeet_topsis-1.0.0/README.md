# **TOPSIS Package**  
_A Python package for decision-making using the TOPSIS method._  

---

## **What is TOPSIS?**  
The **Technique for Order Preference by Similarity to Ideal Solution (TOPSIS)** is a multi-criteria decision analysis method.  
It ranks alternatives based on their closeness to the ideal solution and farthest from the worst solution, making it an excellent tool for decision-making problems.  

---

## **Features**  
- Simple and efficient implementation of the TOPSIS algorithm.  
- Accepts a decision matrix via a CSV file.  
- Supports customizable weights and impacts for criteria.  
- Outputs the TOPSIS scores and ranks into an easy-to-read CSV file.  

---

## **Installation**  
You can install the package from PyPI using:  

```bash
pip install 102217186-abhaijeet-topsis==1.0.0
```

---

## **How to Use**  

### **Run the Package**  

You can run the TOPSIS package directly from the command line using:  

```bash
python -m 102217186_abhaijeet_topsis <input_file> <weights> <impacts> <output_file>
```

### **Parameters**  
- `<input_file>`: Path to the CSV file containing the decision matrix.  
- `<weights>`: Comma-separated weights for each criterion (e.g., `0.2,0.1,0.43,0.3`).  
- `<impacts>`: Comma-separated impacts for each criterion (e.g., `+,+,-,-`, where `+` indicates a benefit criterion and `-` indicates a cost criterion).  
- `<output_file>`: Path to the output CSV file where the results will be saved.  

---

## **Example Usage**  

### Input CSV (`input.csv`)  
```csv
Fund Name,P1,P2,P3,P4,P5
M1,0.91,0.83,6,53,15.19
M2,0.88,0.77,4.1,61.1,16.71
M3,0.67,0.45,3.5,59.4,16.01
M4,0.83,0.69,4.8,44.9,12.81
M5,0.74,0.55,6.7,66.3,18.57
M6,0.6,0.36,4,37.8,10.69
M7,0.72,0.52,4.4,40.7,11.59
M8,0.73,0.53,4.4,66.8,18.12

```  

### Command  
```bash
python -m 102217186_abhaijeet_topsis input.csv "0.2,0.1,0.4,0.3" "+,+,-,+"
output.csv
```

### Output CSV (`output.csv`)  
```csv
Fund Name,P1,P2,P3,P4,P5,TOPSIS Score,Rank
M1,0.91,0.83,6,53,15.19,0.7521,2
M2,0.88,0.77,4.1,61.1,16.71,0.8256,1
M3,0.67,0.45,3.5,59.4,16.01,0.4823,6
M4,0.83,0.69,4.8,44.9,12.81,0.6332,4
M5,0.74,0.55,6.7,66.3,18.57,0.6789,3
M6,0.6,0.36,4,37.8,10.69,0.3145,8
M7,0.72,0.52,4.4,40.7,11.59,0.4012,7
M8,0.73,0.53,4.4,66.8,18.12,0.5798,5

```  

---

## **How It Works**  
1. **Normalization**: The decision matrix is normalized to bring all criteria onto a comparable scale.  
2. **Weighting**: Each criterion is multiplied by its corresponding weight.  
3. **Ideal Solutions**: Calculates the ideal best and worst solutions based on the impacts.  
4. **Distance Calculation**: Computes the distance of each alternative from the ideal best and worst solutions.  
5. **Ranking**: Scores and ranks alternatives based on their relative closeness to the ideal solution.  

---

## **License**  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## **Support**  
If you encounter any issues or have questions, feel free to open an issue on [GitHub](https://github.com/yourusername/102217186-abhaijeet-topsis).  

---