#@title punto estático de operación Q5 y Q6
import pandas as pd
from sympy import symbols
from incertidumbres import  agregar_calculo_a_dataframe

df_q5_q6 = pd.read_excel('practica-1-E2.xlsx', sheet_name=0)
print(df_q5_q6)


vc, ve = variables = symbols('vc ve')
f_voltaje_ce = vc - ve
agregar_calculo_a_dataframe(df_q5_q6, f_voltaje_ce, variables, [3, 4, 7, 8], 'Vce')


ve1, ve2, re = variables = symbols('ve1 ve2 re')
f_corriente_e = (ve1 - ve2)/re
agregar_calculo_a_dataframe(df_q5_q6, f_corriente_e, variables, [7, 8, 9, 10,11,12], 'Ie')

print(df_q5_q6)

with pd.ExcelWriter('practica-1-E2-mediciones.xlsx') as writer:
  df_q5_q6.to_excel(writer, sheet_name='Punto operación Q5 Q6')