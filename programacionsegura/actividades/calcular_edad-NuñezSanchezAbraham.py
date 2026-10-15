from datetime import date

MIN_DAY = 1
MAX_DAY = 31
MIN_MONTH = 1
MAX_MONTH = 12
MIN_YEAR = 1900

#Funcion que pide un numero entero entre un rango especifico que se repite hasta que sea valido 
def pedir_numero(nombre, minimo, maximo):
    while True:
        try:
            texto = input(f"Ingresa el {nombre}: ").strip()
            #entrada vacia
            if texto == "":
                raise ValueError("no puede estar vacío.")
            #entrada de un numero negativo
            if texto.startswith("-"):
                raise ValueError("no puede ser negativo.")
            #entrada de un numero con "." o ","
            if "." in texto or "," in texto:
                raise ValueError("debe ser un número entero, sin punto decimal.")
            #entrada de un caracter de texto
            if not texto.isdigit():  # letras, símbolos, espacios intermedios, etc.
                raise ValueError("solo puede contener dígitos (sin letras ni símbolos).")

            #manejo de errores si se pasa del rango establecido
            valor = int(texto)
            if not minimo <= valor <= maximo:
                raise ValueError(f"debe estar entre {minimo} y {maximo}.")
            return valor

        except ValueError as e:
            print(f"  Error: el {nombre} {e}")


def calcular_edad(day, month, year, hoy=None):
    """Regresa la edad en años cumplidos. Lanza ValueError si la fecha no es válida."""
    hoy = hoy or date.today()
    nacimiento = date(year, month, day)  # ValueError si no existe (ej. 31/02)
    if nacimiento > hoy:
        raise ValueError("la fecha de nacimiento no puede ser posterior a hoy.")
    edad = hoy.year - year
    if (hoy.month, hoy.day) < (month, day):
        edad -= 1  # todavía no cumple años este año
    return edad


def menu():
    print("Calculadora de edad")
    try:
        while True:
            day = pedir_numero("día", MIN_DAY, MAX_DAY)
            month = pedir_numero("mes", MIN_MONTH, MAX_MONTH)
            year = pedir_numero("año", MIN_YEAR, date.today().year)
            try:
                edad = calcular_edad(day, month, year)
            except ValueError as e:
                msg = str(e)
                if "posterior" not in msg:
                    msg = f"la fecha {day:02d}/{month:02d}/{year} no existe en el calendario."
                print(f"  Error: {msg} Intenta de nuevo.\n")
                continue
            print(f"\nTienes {edad} año{'s' if edad != 1 else ''}.")
            break
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma cancelado.")


if __name__ == "__main__":
    menu()
