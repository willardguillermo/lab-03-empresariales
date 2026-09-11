# Quiz App — Laboratorio de Desarrollo de Aplicaciones Empresariales

GUILLERMO JHERICO WILLARD CASTILLO

## Descripción del laboratorio

Este proyecto implementa una aplicación de exámenes (quiz) en Django,
desarrollada como laboratorio del curso Desarrollo de Aplicaciones
Empresariales. Incluye:

- Los modelos `Exam`, `Question` y `Choice`, con sus relaciones
  (`Exam` → `Question` → `Choice`) y sus migraciones correspondientes.
- Formularios (`ExamForm`, `QuestionForm`) y un formset en línea
  (`ChoiceFormSet`) que permite crear una pregunta junto con sus
  cuatro opciones de respuesta en una sola página.
- Una vista (`question_create`) que valida, además de los campos
  individuales, una regla de negocio propia del dominio: cada
  pregunta debe tener **exactamente una** opción marcada como
  correcta.
- Registro de los tres modelos en el panel de administración de
  Django, con un inline para editar las opciones de una pregunta
  desde la misma página.
- Un management command (`seed_quiz_data`) para poblar la base de
  datos con datos de prueba de forma reproducible.

## Instalación y ejecución

Los siguientes comandos se ejecutan desde la raíz del proyecto.

1. **Crear y activar el entorno virtual:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   (en Linux/macOS: `python3 -m venv venv && source venv/bin/activate`)

2. **Instalar las dependencias:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Configurar las variables de entorno:** copiar `.env.example` a
   `.env` y ajustar los valores si hace falta (`SECRET_KEY`, `DEBUG`,
   `ALLOWED_HOSTS`).

4. **Aplicar las migraciones:**

   ```powershell
   python src\manage.py migrate
   ```

5. **Crear un superusuario** (para acceder al panel de admin):

   ```powershell
   python src\manage.py createsuperuser
   ```

6. **Levantar el servidor de desarrollo:**

   ```powershell
   python src\manage.py runserver
   ```

7. **(Opcional) Cargar datos de prueba** con el management command,
   en vez de cargarlos a mano desde el admin:

   ```powershell
   python src\manage.py seed_quiz_data
   ```

   Este comando es idempotente: se puede correr varias veces sin
   duplicar el examen de ejemplo ni sus preguntas/opciones.

La aplicación queda disponible en `http://127.0.0.1:8000/quiz/`, y el
panel de administración en `http://127.0.0.1:8000/admin/`.

## Justificación de los tipos de campo

### Modelo `Exam`

- **`title = models.CharField(max_length=200)`** — El título de un
  examen es un texto corto y de longitud acotada por naturaleza.
  `CharField` obliga a definir un límite máximo (`max_length`), lo
  cual es apropiado aquí porque no tiene sentido permitir títulos
  arbitrariamente largos, y además se traduce en una columna
  `VARCHAR` más eficiente que un `TEXT` sin límite.
- **`description = models.TextField()`** — La descripción de un
  examen puede ser un párrafo largo con instrucciones o contexto,
  sin un límite de longitud razonable a priori. `TextField` no
  impone `max_length`, por lo que es el tipo adecuado para contenido
  de longitud variable y potencialmente extensa.
- **`created_at = models.DateTimeField(auto_now_add=True)`** — Se
  necesita registrar automáticamente el momento exacto de creación
  del examen, sin que el usuario pueda editarlo manualmente.
  `auto_now_add=True` hace que Django asigne la fecha y hora actuales
  solo una vez, en el momento de la creación del registro. Se eligió
  `DateTimeField` en vez de `DateField` para conservar también la
  hora, útil para poder ordenar los exámenes cronológicamente con
  precisión (`ordering = ['-created_at']`).

### Modelo `Question`

- **`text = models.TextField()`** — El enunciado de una pregunta
  puede ser largo (una descripción, un caso, varias oraciones), por
  lo que, igual que en `Exam.description`, se prefiere `TextField`
  sobre `CharField` para no imponer un límite artificial de
  caracteres.
- **`exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')`**
  — Representa la relación de muchos-a-uno entre preguntas y su
  examen (una pregunta pertenece a exactamente un examen, un examen
  tiene muchas preguntas). Se usa `on_delete=models.CASCADE` para
  que, si se elimina un examen, sus preguntas se eliminen
  automáticamente con él, evitando registros huérfanos e
  inconsistencias referenciales. `related_name='questions'` permite
  acceder a las preguntas de un examen con `exam.questions.all()`.
- **`score = models.PositiveIntegerField(default=1)`** — El puntaje
  de una pregunta se expresa naturalmente como un número entero de
  puntos (1, 2, 5, etc.), no como un valor fraccionario, por lo que
  se prefirió un tipo entero sobre `DecimalField`. Se usó
  específicamente `PositiveIntegerField` (en vez de `IntegerField`)
  porque un puntaje negativo no tiene sentido de negocio y así la
  propia base de datos/formularios lo impiden. El `default=1` fue
  necesario porque este campo se agregó en una migración posterior
  (`0002_question_score.py`) cuando ya existían preguntas cargadas en
  la tabla: sin un valor por defecto, Django no podría completar esa
  columna en las filas existentes.

### Modelo `Choice`

- **`text = models.CharField(max_length=200)`** — El texto de una
  opción de respuesta suele ser una frase corta (a diferencia del
  enunciado de la pregunta), por lo que un `CharField` con longitud
  acotada es más apropiado que un `TextField`; además se renderiza
  naturalmente como un `<input type="text">` en los formularios en
  vez de un `<textarea>`.
- **`question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')`**
  — Igual que `Question.exam`, modela la relación de muchos-a-uno
  entre opciones y su pregunta. `on_delete=models.CASCADE` asegura
  que, al borrar una pregunta, sus opciones se eliminen junto con
  ella. `related_name='choices'` habilita `question.choices.all()`.
- **`is_correct = models.BooleanField(default=False)`** — Marcar si
  una opción es la respuesta correcta es, por definición, un valor de
  verdadero/falso, así que `BooleanField` es el tipo natural (no un
  `CharField` con "sí"/"no", ni un entero como bandera). El
  `default=False` obliga a marcar explícitamente cuál opción es la
  correcta en vez de asumir que lo es por omisión, lo cual es más
  seguro de cara a la regla de negocio de "exactamente una opción
  correcta por pregunta" que implementa la vista `question_create`.

## Migraciones

El proyecto tiene dos migraciones en la app `quiz`:

- **`0001_initial.py`**: crea las tres tablas del dominio
  (`quiz_exam`, `quiz_question`, `quiz_choice`) mediante tres
  operaciones `migrations.CreateModel`, una por modelo, en orden de
  dependencia (`Exam` primero, luego `Question` que depende de
  `Exam`, y por último `Choice` que depende de `Question`). No tiene
  `dependencies` porque es la primera migración de la app.

- **`0002_question_score.py`**: agrega el campo `score` al modelo
  `Question` ya existente, mediante una única operación
  `migrations.AddField`. Django elige `AddField` en vez de
  `CreateModel` porque compara el estado de los modelos contra la
  última migración aplicada (`0001_initial`) y detecta que `Question`
  ya existía; lo único nuevo es un atributo agregado a esa misma
  clase. Esta migración sí declara `dependencies = [('quiz',
  '0001_initial')]`, ya que la tabla `quiz_question` debe existir
  antes de poder agregarle una columna.

  Como la tabla ya tenía filas cargadas al momento de generar esta
  migración, fue necesario definir `score` con `default=1` en el
  modelo. Al aplicar `migrate`, Django ejecuta el equivalente a
  `ALTER TABLE quiz_question ADD COLUMN score integer unsigned NOT
  NULL DEFAULT 1`, lo que rellena automáticamente la columna nueva en
  todas las filas existentes sin perder ninguna fila ni ningún otro
  dato (`text`, `exam_id` quedan intactos).

## Casos de prueba

La aplicación se probó con tres estrategias complementarias:

1. **Carga manual desde el admin:** se creó un superusuario con
   `createsuperuser` y, desde `http://127.0.0.1:8000/admin/`, se
   registró un examen, dos preguntas asociadas y cuatro opciones por
   pregunta (marcando una sola como correcta en cada caso),
   aprovechando el `ChoiceInline` configurado en `QuestionAdmin` para
   editar las opciones en la misma página que la pregunta.

2. **Carga automática con `seed_quiz_data`:** se ejecutó el
   management command para poblar un examen de ejemplo
   ("Django Fundamentals Quiz") con 6 preguntas y 4 opciones cada
   una. Se corrió el comando dos veces seguidas para confirmar que es
   idempotente: no duplica el examen (se busca por `title` con
   `get_or_create`) ni sus preguntas/opciones (se eliminan y
   recrean gracias a la relación `on_delete=CASCADE`).

3. **Validación de "exactamente una opción correcta"** en la vista
   `question_create`:
   - Si se envía el formulario con **cero** opciones marcadas como
     correctas, la vista rechaza el guardado (no se escribe nada en
     la base de datos) y vuelve a mostrar la página con un mensaje de
     error (`"Exactly one choice must be marked as correct (found
     0)."`), conservando el texto de la pregunta y de las opciones
     que el usuario ya había escrito.
   - Si se marcan **dos o más** opciones como correctas, ocurre lo
     mismo: se rechaza el guardado y se muestra el error indicando
     cuántas opciones correctas se detectaron.
   - Solo cuando hay **exactamente una** opción correcta entre las
     opciones no vacías del formset, la vista guarda la pregunta y
     sus opciones en una sola operación y redirige al detalle del
     examen (`exam_detail`).

## Capturas de pantalla

<img width="1015" height="497" alt="image" src="https://github.com/user-attachments/assets/595a1d2c-166d-42f2-8ee4-89f566d45830" />

<img width="1211" height="590" alt="image" src="https://github.com/user-attachments/assets/5ae46519-8b4e-405b-b677-3118ef52e715" />

<img width="1440" height="811" alt="image" src="https://github.com/user-attachments/assets/d81d8c56-5db1-4577-a224-bfffd97d33e5" />

<img width="494" height="965" alt="image" src="https://github.com/user-attachments/assets/1eec78ee-00f4-49af-9a1e-574f61509dbe" />

<img width="478" height="180" alt="image" src="https://github.com/user-attachments/assets/333fe1ba-1b94-4a6e-b028-9c97f53ca45e" />



## Conclusiones

1. Declarar los modelos Exam, Question y Choice con el tipo de campo correcto para cada atributo (TextField para contenido largo, CharField para texto corto, BooleanField para banderas de verdadero/falso, ForeignKey con on_delete=CASCADE para relaciones de dependencia) permitió que Django generara automáticamente una base de datos consistente, sin necesidad de escribir SQL manualmente ni preocuparse por la integridad referencial entre exámenes, preguntas y opciones.
   
2. Las migraciones de Django no son un paso mecánico, sino un historial versionado de cómo evolucionó el modelo de datos: la primera migración (0001_initial.py) creó las tres tablas desde cero, mientras que la segunda (0002_question_score.py) solo agregó una columna a una tabla existente, usando AddField en vez de CreateModel, y requiriendo un valor por defecto para no romper las filas que ya tenían datos. Entender esta diferencia es clave para modificar un proyecto en producción sin perder información.
   
3. Los formsets resuelven un problema que un ModelForm normal no puede: validar y guardar en una sola operación un conjunto de objetos dependientes de otro (las 4 opciones de una pregunta). La regla de negocio "exactamente una opción correcta" no se puede expresar a nivel de un solo formulario, sino que debe evaluarse sobre el formset completo después de que Django valide cada formulario individualmente, lo que refuerza la diferencia entre validación de datos (tipos, campos requeridos) y validación de reglas de negocio (lógica propia de la aplicación).
