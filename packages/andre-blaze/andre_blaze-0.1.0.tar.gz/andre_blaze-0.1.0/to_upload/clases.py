class Libros:
    def __init__(self, titulo, descripcion):
        self.titulo = titulo
        self.descripcion = descripcion

    def __repr__(self):
        return f"[*] {self.titulo}\n {self.descripcion}\n"


libros = [
    Libros("Hábitos atómicos", "Esta es la descripción de hábitos atomicos"),
    Libros(
        "Si lo crees lo creas",
        "Librazo hermano, cuando me termine de leer de cero a uno voy a empezar a leerlo",
    ),
    Libros(
        "__str__ y __repr__", "Métodos especiales para python, string y representation"
    ),
]

# print(dir(Libros))


# for value in dir(Libros):
# print(value)

# for libro in libros:
#     print(libro)
