# Topsis-KrishnaVig-102217119

Assignment(UCS654)<br>
Submitted by: Krishna Vig<br>
Roll no: 102217119<br>
Group: 3Q14

## Description

This is a python package used to implement TOPSIS(Technique of Order Preference Similarity to the Ideal Solution) for MCDA(Multiple criteria decision analysis)

<br>

## How to use this package:

## Installation

pip install Topsis-KrishnaVig-102217119

## Example:

## Sample dataset

|P1|P2|P3|P4|P5|
|---|---|---|---|---|
|0\.84|0\.71|6\.7|42\.1|12\.59|
|0\.91|0\.83|7\.0|31\.7|10\.11|
|0\.79|0\.62|4\.8|46\.7|13\.23|
|0\.78|0\.61|6\.4|42\.4|12\.55|
|0\.94|0\.88|3\.6|62\.2|16\.91|
|0\.88|0\.77|6\.5|51\.5|14\.91|
|0\.66|0\.44|5\.3|48\.9|13\.83|
|0\.93|0\.86|3\.4|37\.0|10\.55|
## Input

### In Command Prompt

Enter filename followed by .csv or .xlsx extension, then enter values of weights separated by commas like "1,1,1,2,2",then enter values of impacts separated by commas like "+,+,-,-,+" without giving space in between comma value, then enter name of file where you want to save output followed by .csv extension

```
python -m Topsis_KrishnaVig_102217119 data.xlsx "1,1,1,1,1" "+,-,+,-,+" output.csv
```

## Output

This will be in our Output csv file
|P1|P2|P3|P4|P5|Topsis Score|Rank|
|---|---|---|---|---|---|---|
|0\.84|0\.71|6\.7|42\.1|12\.59|0\.5945517248616172|2|
|0\.91|0\.83|7\.0|31\.7|10\.11|0\.5662461787825045|3|
|0\.79|0\.62|4\.8|46\.7|13\.23|0\.4853941230447056|6|
|0\.78|0\.61|6\.4|42\.4|12\.55|0\.6127758823558636|1|
|0\.94|0\.88|3\.6|62\.2|16\.91|0\.36155091758331526|8|
|0\.88|0\.77|6\.5|51\.5|14\.91|0\.5387640655736284|5|
|0\.66|0\.44|5\.3|48\.9|13\.83|0\.560458620506467|4|
|0\.93|0\.86|3\.4|37\.0|10\.55|0\.38966293040831607|7|