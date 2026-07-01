# hunterclassic - Librería Python para TheHunter Classic

Una librería Python completamente tipada y orientada a objetos para interactuar con la API de TheHunter Classic, con un módulo de datos estáticos robusto y extensible.

## Características

- ✅ **Tipado estricto** - Python 3.12 + Pydantic v2
- ✅ **Arquitectura limpia** - Separación de responsabilidades, bajo acoplamiento
- ✅ **Consultas O(1)** - Índices optimizados para todas las búsquedas
- ✅ **Inmutabilidad** - Todos los modelos son frozen, sin efectos secundarios
- ✅ **Validación completa** - Integridad de datos y referencias cruzadas
- ✅ **Cache inteligente** - Carga única de datos estáticos
- ✅ **Extensible** - Fácil agregar nuevos tipos de datos (misiones, logros, etc.)
- ✅ **API elegante** - Diseñada para ser usada por otros desarrolladores

## Instalación

```bash
pip install pydantic
```

La librería no requiere instalación adicional - es código Python puro.

## Estructura del Proyecto

```
hunterclassic/
├── models/                    # Modelos de dominio (Pydantic)
│   ├── animal.py             # Animal (Alce, Ciervo, etc.)
│   ├── weapon.py             # Arma (Rifle, Escopeta, etc.)
│   ├── ammo.py               # Munición
│   ├── reserve.py            # Reserva (Hirschfelden, etc.)
│   ├── loadout.py            # Combinación ética arma+municion
│   └── __init__.py
├── static/                    # Datos JSON del juego
│   ├── animals.json          # 62 animales con municiones éticas
│   ├── weapons.json          # 138 armas con municiones compatibles
│   └── reserves.json         # 12 reservas con especies
└── static_data/              # Sistema de datos estáticos
    ├── loader.py             # Carga y parseo de JSON
    ├── validator.py          # Validación de integridad
    ├── repository.py         # BaseRepository genérico
    ├── repositories.py       # Repositorios específicos
    ├── static_data.py        # API pública principal
    ├── cache.py              # Cache de datos
    ├── static_files.py       # Contenedor de datos
    └── __init__.py           # Exportaciones públicas
```

## Uso Rápido

```python
from hunterclassic.static_data import StaticData

# Cargar todos los datos estáticos
static = StaticData.load()

# Consultas básicas
animal = static.animals.get(55)                    # Gamo
arma = static.weapons.get(296)                     # Rifle de Cerrojo .300
reserva = static.reserves.get(5)                   # Hirschfelden

# Búsquedas por diferentes criterios
animal = static.animals.get_by_define("FALLOW_DEER")
animal = static.animals.get_by_name("Gamo")
reserva = static.reserves.get_by_define("GERMAN_FARMLANDS")

# Obtener todos los elementos
todos_animales = static.animals.all()              # tuple[Animal, ...]
todas_armas = static.weapons.all()
todas_reservas = static.reserves.all()
```

## Consultas Avanzadas

### Relaciones entre entidades

```python
# Animal ↔ Reserva
fallow = static.animals.get_by_define("FALLOW_DEER")
hirschfelden = static.reserves.get(5)

# ¿Está el animal en la reserva?
print(static.reserves.contains(hirschfelden, fallow))      # True
print(static.animals.available_in(fallow, hirschfelden))   # True

# Todos los animales de una reserva
animales_en_hirsch = static.reserves.animals_in(hirschfelden, static.animals)
# ['Faisán', 'Jabalí', 'Corzo', 'Ciervo Rojo', ...]

# Todas las reservas donde aparece un animal
reservas_del_fallow = static.reserves.reserves_for(fallow)
# ['Hirschfelden']
```

### Armas y Municiones Éticas

```python
# Municiones éticas para un animal
municiones_eticas = static.animals.ethical_ammo_for(fallow, static.ammo)
# 40 tipos de munición

# Armas que tienen al menos una munición ética
armas_eticas = static.weapons.ethical_weapons_for(fallow)
# 107 armas diferentes

# Todas las combinaciones (arma, munición) éticas
loadouts = static.weapons.ethical_loadouts_for(fallow)
# 161 combinaciones únicas

# Verificar compatibilidad
arma_300 = static.weapons.get(296)
municion_300 = static.ammo.get(11)

print(static.weapons.supports(arma_300, municion_300))     # True
print(static.weapons.supports_animal(arma_300, fallow))    # True
print(static.animals.is_ethical(fallow, municion_300))     # True
```

### Cache para múltiples usos

```python
from hunterclassic.static_data import StaticDataCache

# Cache explícito (recomendado para aplicaciones)
cache = StaticDataCache()
static1 = cache.get()      # Carga desde disco
static2 = cache.get()      # Reutiliza instancia cacheada

# Forzar recarga si los datos cambian
cache.invalidate()
static3 = cache.get()      # Carga nueva instancia
```

## Integración con el Cliente Existente

```python
# En tu clase Client existente
from hunterclassic.static_data import StaticDataCache

class HunterClassicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._static_cache = StaticDataCache()
    
    @property
    def static(self):
        """Acceso a datos estáticos del juego"""
        return self._static_cache.get()

# Uso
client = HunterClassicClient(api_key="tu_api_key")
client.static.animals.get(55)
client.static.weapons.get(296)
client.static.reserves.get(5)
```

## Modelos de Datos

### Animal
```python
class Animal(BaseModel):
    id: int                    # 55
    name: str                  # "Gamo"
    short: str                 # "fallow_deer"
    define: str                # "FALLOW_DEER"
    ethical_ammo_ids: frozenset[int]  # {11, 113, 370, ...}
```

### Weapon
```python
class Weapon(BaseModel):
    id: int                    # 296
    name: str                  # "Rifle de Cerrojo .300"
    shortname: str             # ".300 Rifle"
    image: str                 # "rifle_300_02"
    ammo: tuple[Ammo, ...]     # Municiones compatibles
```

### Reserve
```python
class Reserve(BaseModel):
    id: int                    # 5
    name: str                  # "Hirschfelden"
    define: str                # "GERMAN_FARMLANDS"
    species_ids: frozenset[int]  # {7, 10, 11, 12, ...}
```

### EthicalLoadout (Value Object)
```python
class EthicalLoadout(BaseModel):
    weapon: Weapon
    ammo: Ammo
```

## Extendiendo el Sistema

Para agregar nuevos tipos de datos (misiones, logros, objetos coleccionables):

### 1. Crear el modelo
```python
# hunterclassic/models/mission.py
class Mission(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    name: str
    map_id: int      # Referencia a Reserve.id
    objective: str
    reward_xp: int
```

### 2. Agregar JSON en `static/`
```json
// missions.json
[
  {
    "id": 1,
    "name": "Cazar 3 ciervos",
    "mapId": 5,
    "objective": "Cazar 3 ciervos en Hirschfelden",
    "rewardXp": 1000
  }
]
```

### 3. Extender el Loader
```python
# En StaticDataLoader
def _parse_missions(self, raw: list[dict]) -> tuple[Mission, ...]:
    return tuple(Mission(...) for item in raw)
```

### 4. Crear Repository
```python
class MissionRepository(BaseRepository[Mission]):
    def __init__(self, missions: tuple[Mission, ...]):
        super().__init__(missions)
        self._by_map_id: dict[int, list[Mission]] = {}
        # Construir índices personalizados
    
    def get_by_map(self, map_id: int) -> list[Mission]:
        return self._by_map_id.get(map_id, [])
```

### 5. Actualizar StaticData
```python
class StaticData:
    def __init__(self, files: StaticFiles):
        self._missions = MissionRepository(files.missions)
        # ... repositorios existentes
    
    @property
    def missions(self) -> MissionRepository:
        return self._missions
```

Ver `hunterclassic/static_data/EXTENDING.md` para guía completa.

## Validaciones Automáticas

El sistema valida automáticamente:

- **IDs duplicados** dentro de cada colección
- **Defines duplicados** (nombres únicos del juego)
- **Referencias rotas** (municiones éticas que no existen)
- **Especies inexistentes** en reservas
- **Integridad JSON** (encoding, estructura)

Cualquier inconsistencia lanza `ValueError` con mensaje descriptivo.

## Rendimiento

- **Carga inicial**: ~100ms (depende del disco)
- **Consultas**: Todas O(1) después de la carga
- **Memoria**: ~5-10 MB para todos los datos
- **Cache**: Los datos se mantienen en memoria mientras viva el cache

## Casos de Uso Típicos

### 1. Calculadora de Loadouts Éticos
```python
def calcular_loadouts_para_animal(animal: Animal) -> list[EthicalLoadout]:
    """Devuelve todas las combinaciones éticas para un animal"""
    return static.weapons.ethical_loadouts_for(animal)
```

### 2. Verificador de Equipamiento
```python
def verificar_equipamiento(arma: Weapon, municion: Ammo, animal: Animal) -> bool:
    """Verifica si un equipamiento es ético para un animal"""
    return (
        static.weapons.supports(arma, municion) and
        static.animals.is_ethical(animal, municion)
    )
```

### 3. Planificador de Cacería
```python
def animales_en_reserva_con_armas(reserva: Reserve) -> dict[Animal, list[Weapon]]:
    """Para cada animal en la reserva, lista armas éticas disponibles"""
    resultado = {}
    for animal in static.reserves.animals_in(reserva, static.animals):
        resultado[animal] = static.weapons.ethical_weapons_for(animal)
    return resultado
```

## Limitaciones

- **Datos estáticos solamente** - No incluye datos dinámicos (estadísticas de jugador, inventario)
- **Solo tres tipos iniciales** - Animals, Weapons, Reserves (pero extensible)
- **Encoding de nombres** - Algunos nombres en weapons.json tienen encoding corrupto (problema del origen)

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

MIT License - ver LICENSE para detalles.

## Créditos

- Datos obtenidos mediante ingeniería inversa del cliente oficial de TheHunter Classic
- Diseño inspirado en Domain-Driven Design y Clean Architecture
- Desarrollado con Python 3.12 y Pydantic v2

## Soporte

Para issues, preguntas o sugerencias:
- Abre un issue en GitHub
- Consulta la documentación en `hunterclassic/static_data/EXTENDING.md`
- Revisa los ejemplos en `hunterclassic/static_data/mission_repository_example.py`
