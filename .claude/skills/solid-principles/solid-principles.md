---
name: solid-principles
description: >
  Aplica, revisa y enseña los principios SOLID en código orientado a objetos.
  Usa esta skill cuando el usuario pida revisar si su código cumple SOLID, refactorizar
  código para que sea más SOLID, explicar alguno de los 5 principios con ejemplos,
  detectar violaciones de SOLID en clases o módulos, o diseñar arquitectura limpia
  basada en SOLID. Activa también ante palabras clave como "single responsibility",
  "open/closed", "liskov", "interface segregation", "dependency inversion",
  "acoplamiento", "cohesión", "herencia", "abstracción", "refactorizar clases",
  o cuando el usuario diga "¿esto está bien diseñado?", "¿cómo mejoro este código?",
  "el código huele mal", o "code smell".
---

# SOLID Principles Skill

## Objetivo

Ayudar al usuario a entender, aplicar y auditar los 5 principios SOLID en su código,
con ejemplos concretos, detección de violaciones y propuestas de refactorización.

---

## Los 5 Principios

### S — Single Responsibility Principle (SRP)
> "Una clase debe tener una sola razón para cambiar."

Una clase hace **una sola cosa** y la hace bien. Si necesitas usar "y" para describir
lo que hace una clase, probablemente viola SRP.

**Señales de violación:**
- La clase tiene métodos de lógica de negocio, acceso a base de datos Y formateo de respuesta
- El nombre de la clase es genérico: `Manager`, `Handler`, `Utils`, `Helper`
- Cambiar una funcionalidad rompe otra no relacionada

**Antes (viola SRP):**
```python
class UserService:
    def create_user(self, data): ...
    def send_welcome_email(self, user): ...   # ← responsabilidad de emails
    def save_to_database(self, user): ...      # ← responsabilidad de persistencia
    def format_user_response(self, user): ... # ← responsabilidad de presentación
```

**Después (cumple SRP):**
```python
class UserService:
    def create_user(self, data): ...

class EmailService:
    def send_welcome_email(self, user): ...

class UserRepository:
    def save(self, user): ...

class UserSerializer:
    def to_response(self, user): ...
```

---

### O — Open/Closed Principle (OCP)
> "El software debe estar abierto para extensión, pero cerrado para modificación."

Puedes **agregar** comportamiento nuevo sin **modificar** el código existente.
Se logra mediante abstracciones (interfaces, clases base, estrategias).

**Señales de violación:**
- `if tipo == "A": ... elif tipo == "B": ...` en lógica de negocio
- Agregar una nueva variante requiere modificar múltiples archivos
- Switch/match sobre tipos en lugar de polimorfismo

**Antes (viola OCP):**
```python
class ReportGenerator:
    def generate(self, type: str, data):
        if type == "pdf":
            # generar PDF
        elif type == "excel":
            # generar Excel
        elif type == "csv":   # ← cada nuevo formato modifica esta clase
            # generar CSV
```

**Después (cumple OCP):**
```python
from abc import ABC, abstractmethod

class ReportStrategy(ABC):
    @abstractmethod
    def generate(self, data): ...

class PdfReport(ReportStrategy):
    def generate(self, data): ...

class ExcelReport(ReportStrategy):
    def generate(self, data): ...

class ReportGenerator:
    def __init__(self, strategy: ReportStrategy):
        self.strategy = strategy

    def generate(self, data):
        return self.strategy.generate(data)
# Para agregar CSV: solo creas CsvReport, sin tocar nada más ✓
```

---

### L — Liskov Substitution Principle (LSP)
> "Los objetos de una subclase deben poder reemplazar a los de la clase base sin romper el programa."

Si tienes una función que recibe un `Animal`, debe funcionar igual si le pasas un `Perro` o un `Gato`.
La herencia no es solo "reutilizar código", sino modelar una relación **es-un** real.

**Señales de violación:**
- Una subclase lanza excepciones en métodos heredados (`raise NotImplementedError`)
- Tienes `isinstance()` checks para saber qué subclase es
- La subclase ignora o vacía métodos del padre

**Antes (viola LSP):**
```python
class Bird:
    def fly(self): ...

class Penguin(Bird):
    def fly(self):
        raise Exception("Los pingüinos no vuelan") # ← rompe LSP
```

**Después (cumple LSP):**
```python
class Bird:
    def move(self): ...

class FlyingBird(Bird):
    def fly(self): ...

class Penguin(Bird):
    def move(self): # nada, camina/nada
        ...

class Eagle(FlyingBird):
    def fly(self): ...
```

---

### I — Interface Segregation Principle (ISP)
> "Los clientes no deben depender de interfaces que no usan."

Es mejor tener muchas interfaces pequeñas y específicas que una sola interfaz grande y genérica.

**Señales de violación:**
- Una interfaz/clase base tiene métodos que algunas subclases implementan como `pass` o `raise NotImplementedError`
- Las clases implementan métodos que no necesitan solo para cumplir un contrato

**Antes (viola ISP):**
```python
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...   # ← un robot no come
    @abstractmethod
    def sleep(self): ... # ← un robot no duerme

class Robot(Worker):
    def work(self): ...
    def eat(self): raise NotImplementedError  # ← forced
    def sleep(self): raise NotImplementedError  # ← forced
```

**Después (cumple ISP):**
```python
class Workable(ABC):
    @abstractmethod
    def work(self): ...

class Eatable(ABC):
    @abstractmethod
    def eat(self): ...

class Robot(Workable):
    def work(self): ...

class Human(Workable, Eatable):
    def work(self): ...
    def eat(self): ...
```

---

### D — Dependency Inversion Principle (DIP)
> "Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones."

Las clases no deben crear sus propias dependencias internamente (`new`, instanciación directa).
Deben recibirlas desde afuera (inyección de dependencias).

**Señales de violación:**
- `self.db = MySQLDatabase()` dentro del constructor de un servicio
- Imposible hacer tests sin una base de datos real
- Cambiar la implementación concreta obliga a modificar la clase de alto nivel

**Antes (viola DIP):**
```python
class OrderService:
    def __init__(self):
        self.db = PostgreSQLDatabase()  # ← acoplado a implementación concreta
        self.mailer = SendGridMailer()  # ← acoplado a proveedor específico

    def place_order(self, order):
        self.db.save(order)
        self.mailer.send(order.user.email, "Tu pedido fue confirmado")
```

**Después (cumple DIP):**
```python
class Database(ABC):
    @abstractmethod
    def save(self, entity): ...

class Mailer(ABC):
    @abstractmethod
    def send(self, to: str, message: str): ...

class OrderService:
    def __init__(self, db: Database, mailer: Mailer): # ← recibe abstracciones
        self.db = db
        self.mailer = mailer

    def place_order(self, order):
        self.db.save(order)
        self.mailer.send(order.user.email, "Tu pedido fue confirmado")

# En producción:
service = OrderService(PostgreSQLDatabase(), SendGridMailer())
# En tests:
service = OrderService(InMemoryDatabase(), FakeMailer())
```

---

## Flujo de auditoría de código

Cuando el usuario comparte código para revisar, sigue este orden:

1. **Leer el código completo** antes de emitir juicio
2. **Identificar clases/módulos principales** y sus responsabilidades
3. **Evaluar cada principio** con evidencia concreta del código
4. **Priorizar las violaciones** por impacto (SRP y DIP suelen ser las más críticas)
5. **Proponer refactorización** con código concreto, no solo teoría
6. **Explicar el beneficio** de cada cambio propuesto (testabilidad, extensibilidad, etc.)

### Formato de reporte sugerido

```
## Auditoría SOLID

### ✅ SRP — Cumple
[breve justificación]

### ⚠️ OCP — Violación detectada
**Dónde:** [clase/método específico]
**Problema:** [explicación]
**Solución propuesta:** [código]

### ✅ LSP — Cumple
...
```

---

## Notas importantes

- **SOLID no es dogma**: en proyectos pequeños o scripts, aplicar todos los principios
  puede ser sobreingeniería. Menciona esto si el contexto lo amerita.
- **El lenguaje importa**: adapta los ejemplos al lenguaje del usuario
  (Python, TypeScript, Java, C#, etc.)
- **SRP + DIP primero**: son los de mayor impacto en testabilidad y mantenibilidad.
  Si hay poco tiempo, empieza por ahí.
- **No refactorices todo a la vez**: prioriza y propón cambios incrementales.
