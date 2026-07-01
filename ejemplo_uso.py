"""
Ejemplo completo de uso de hunterclassic.static_data

Este archivo demuestra todas las capacidades del sistema de datos estáticos.
"""

from hunterclassic.static_data import StaticData, StaticDataCache


def ejemplo_basico():
    """Ejemplos básicos de consulta"""
    print("=== EJEMPLO BÁSICO ===")
    
    # Cargar datos (una sola vez)
    static = StaticData.load()
    
    # 1. Consultas por ID
    animal = static.animals.get(55)
    print(f"Animal ID 55: {animal.name} ({animal.define})")
    
    arma = static.weapons.get(296)
    print(f"Arma ID 296: {arma.name} ({arma.shortname})")
    
    reserva = static.reserves.get(5)
    print(f"Reserva ID 5: {reserva.name} ({reserva.define})")
    
    municion = static.ammo.get(11)
    print(f"Municion ID 11: {municion.name}")
    
    # 2. Consultas por define/name
    fallow = static.animals.get_by_define("FALLOW_DEER")
    print(f"FALLOW_DEER: {fallow.name}")
    
    gamo = static.animals.get_by_name("Gamo")
    print(f"Animal 'Gamo': {gamo.define}")
    
    hirschfelden = static.reserves.get_by_define("GERMAN_FARMLANDS")
    print(f"GERMAN_FARMLANDS: {hirschfelden.name}")
    
    # 3. Obtener todos los elementos
    print(f"\nTotal animales: {len(static.animals.all())}")
    print(f"Total armas: {len(static.weapons.all())}")
    print(f"Total reservas: {len(static.reserves.all())}")
    print(f"Total tipos de munición: {len(static.ammo.all())}")


def ejemplo_relaciones():
    """Ejemplos de relaciones entre entidades"""
    print("\n=== EJEMPLO RELACIONES ===")
    
    static = StaticData.load()
    fallow = static.animals.get_by_define("FALLOW_DEER")
    hirschfelden = static.reserves.get(5)
    
    # 1. Animal ↔ Reserva
    print(f"¿{fallow.name} está en {hirschfelden.name}?")
    print(f"  reserves.contains(): {static.reserves.contains(hirschfelden, fallow)}")
    print(f"  animals.available_in(): {static.animals.available_in(fallow, hirschfelden)}")
    
    # 2. Todos los animales de una reserva
    animales_en_hirsch = static.reserves.animals_in(hirschfelden, static.animals)
    print(f"\nAnimales en {hirschfelden.name}:")
    for animal in animales_en_hirsch[:5]:  # Mostrar solo 5
        print(f"  - {animal.name}")
    if len(animales_en_hirsch) > 5:
        print(f"  ... y {len(animales_en_hirsch) - 5} más")
    
    # 3. Todas las reservas de un animal
    reservas_del_fallow = static.reserves.reserves_for(fallow)
    print(f"\nReservas donde aparece {fallow.name}:")
    for reserva in reservas_del_fallow:
        print(f"  - {reserva.name}")


def ejemplo_armas_municiones():
    """Ejemplos de armas, municiones y loadouts éticos"""
    print("\n=== EJEMPLO ARMAS Y MUNICIONES ===")
    
    static = StaticData.load()
    fallow = static.animals.get_by_define("FALLOW_DEER")
    arma_300 = static.weapons.get(296)
    municion_300 = static.ammo.get(11)
    
    # 1. Municiones éticas para un animal
    municiones_eticas = static.animals.ethical_ammo_for(fallow, static.ammo)
    print(f"Municiones éticas para {fallow.name}: {len(municiones_eticas)} tipos")
    
    # 2. Armas éticas para un animal
    armas_eticas = static.weapons.ethical_weapons_for(fallow)
    print(f"Armas éticas para {fallow.name}: {len(armas_eticas)} armas")
    
    # 3. Loadouts éticos (combinaciones arma+municion)
    loadouts = static.weapons.ethical_loadouts_for(fallow)
    print(f"Loadouts éticos para {fallow.name}: {len(loadouts)} combinaciones")
    
    # 4. Verificar compatibilidad
    print(f"\nVerificaciones de compatibilidad:")
    print(f"  ¿{arma_300.shortname} soporta {municion_300.name}?")
    print(f"    weapons.supports(): {static.weapons.supports(arma_300, municion_300)}")
    
    print(f"  ¿{arma_300.shortname} tiene munición ética para {fallow.name}?")
    print(f"    weapons.supports_animal(): {static.weapons.supports_animal(arma_300, fallow)}")
    
    print(f"  ¿{municion_300.name} es ética para {fallow.name}?")
    print(f"    animals.is_ethical(): {static.animals.is_ethical(fallow, municion_300)}")
    
    # 5. Agrupar loadouts por arma
    print(f"\nLoadouts agrupados por arma (primeras 3 armas):")
    loadouts_por_arma = {}
    for loadout in loadouts[:20]:  # Mostrar solo 20 loadouts
        loadouts_por_arma.setdefault(loadout.weapon.shortname, []).append(loadout.ammo.name)
    
    for arma_nombre, municiones in list(loadouts_por_arma.items())[:3]:
        print(f"  {arma_nombre}: {len(municiones)} municiones")


def ejemplo_cache():
    """Ejemplo de uso del cache"""
    print("\n=== EJEMPLO CACHE ===")
    
    from hunterclassic.static_data import StaticDataCache
    
    cache = StaticDataCache()
    
    print("Primera llamada a cache.get() - carga desde disco")
    static1 = cache.get()
    print(f"  Cache cargado: {cache.is_loaded}")
    
    print("\nSegunda llamada a cache.get() - reutiliza cache")
    static2 = cache.get()
    print(f"  Misma instancia: {static1 is static2}")
    
    print("\nInvalidar cache y cargar de nuevo")
    cache.invalidate()
    print(f"  Cache cargado después de invalidate: {cache.is_loaded}")
    
    static3 = cache.get()
    print(f"  Nueva instancia: {static1 is not static3}")


def ejemplo_casos_uso_reales():
    """Ejemplos de casos de uso reales"""
    print("\n=== CASOS DE USO REALES ===")
    
    static = StaticData.load()
    
    # Caso 1: Calculadora de loadouts para una cacería específica
    def calcular_loadouts_para_caceria(reserva_id: int, animal_define: str):
        """Calcula todos los loadouts éticos para un animal en una reserva específica"""
        reserva = static.reserves.get(reserva_id)
        animal = static.animals.get_by_define(animal_define)
        
        if not reserva or not animal:
            return []
        
        # Verificar que el animal esté en la reserva
        if not static.animals.available_in(animal, reserva):
            return []
        
        # Obtener loadouts éticos
        return static.weapons.ethical_loadouts_for(animal)
    
    print("1. Calculadora de loadouts para Gamo en Hirschfelden:")
    loadouts = calcular_loadouts_para_caceria(5, "FALLOW_DEER")
    print(f"   {len(loadouts)} loadouts disponibles")
    
    # Caso 2: Verificador de equipamiento
    def verificar_equipamiento(arma_id: int, municion_id: int, animal_define: str) -> dict:
        """Verifica si un equipamiento es válido y ético"""
        arma = static.weapons.get(arma_id)
        municion = static.ammo.get(municion_id)
        animal = static.animals.get_by_define(animal_define)
        
        resultado = {
            "arma_existe": arma is not None,
            "municion_existe": municion is not None,
            "animal_existe": animal is not None,
            "compatible": False,
            "etico": False,
            "valido": False
        }
        
        if arma and municion and animal:
            resultado["compatible"] = static.weapons.supports(arma, municion)
            resultado["etico"] = static.animals.is_ethical(animal, municion)
            resultado["valido"] = resultado["compatible"] and resultado["etico"]
        
        return resultado
    
    print("\n2. Verificador de equipamiento (.300 Rifle + .300 ammo para Gamo):")
    verificacion = verificar_equipamiento(296, 11, "FALLOW_DEER")
    for clave, valor in verificacion.items():
        print(f"   {clave}: {valor}")
    
    # Caso 3: Planificador de reserva
    def planificar_reserva(reserva_id: int):
        """Para cada animal en la reserva, lista armas éticas disponibles"""
        reserva = static.reserves.get(reserva_id)
        if not reserva:
            return {}
        
        plan = {}
        animales = static.reserves.animals_in(reserva, static.animals)
        
        for animal in animales:
            armas_eticas = static.weapons.ethical_weapons_for(animal)
            if armas_eticas:
                plan[animal.name] = [arma.shortname for arma in armas_eticas[:3]]  # Primeras 3
        
        return plan
    
    print("\n3. Planificador para Hirschfelden (primeros 3 animales):")
    plan = planificar_reserva(5)
    for animal_nombre, armas in list(plan.items())[:3]:
        print(f"   {animal_nombre}: {armas}")


def main():
    """Ejecutar todos los ejemplos"""
    print("=" * 60)
    print("EJEMPLOS DE USO - hunterclassic.static_data")
    print("=" * 60)
    
    ejemplo_basico()
    ejemplo_relaciones()
    ejemplo_armas_municiones()
    ejemplo_cache()
    ejemplo_casos_uso_reales()
    
    print("\n" + "=" * 60)
    print("OK - Todos los ejemplos ejecutados correctamente")
    print("=" * 60)


if __name__ == "__main__":
    main()
