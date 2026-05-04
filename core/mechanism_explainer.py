def explain_mechanism(result: dict) -> str:
    substrate = result["substrate_type"]
    reagent = result["reagent_role"]
    reaction = result["reaction_type"]
    confidence = result["confidence"]
    reasoning = result.get("reasoning", "")

    intro = (
        f"El sistema identificó el sustrato como **{substrate}** y el reactivo como "
        f"**{reagent}**. La reacción más probable es **{reaction}** con confianza "
        f"**{confidence}**. {reasoning}\n\n"
    )

    if "SN2" in reaction:
        return intro + "Mecanismo: ataque posterior del nucleófilo y salida simultánea del grupo saliente. Puede haber inversión de configuración."
    if "E2" in reaction:
        return intro + "Mecanismo: la base extrae un H beta mientras sale el grupo saliente, formando un doble enlace."
    if "SN1" in reaction or "E1" in reaction:
        return intro + "Mecanismo: salida del grupo saliente, formación de carbocatión y posterior sustitución o eliminación."
    if "Adición electrofílica" in reaction:
        return intro + "Mecanismo: el enlace pi ataca al electrófilo y después entra un nucleófilo."
    if "Halogenación" in reaction:
        return intro + "Mecanismo: formación de ion halonio y ataque anti del haluro."
    if "Oxidación" in reaction:
        return intro + "Mecanismo general: aumento del estado de oxidación del carbono unido al oxígeno."
    if "Reducción" in reaction:
        return intro + "Mecanismo: donación de hidruro al carbonilo y posterior protonación."
    if "Grignard" in reaction:
        return intro + "Mecanismo: ataque nucleofílico carbonado al carbonilo y protonación final."
    if "Sustitución electrofílica aromática" in reaction:
        return intro + "Mecanismo: ataque del anillo al electrófilo, complejo sigma y recuperación de aromaticidad."
    if "Esterificación" in reaction:
        return intro + "Mecanismo: activación ácida del carbonilo, ataque del alcohol y pérdida de agua."
    if "Hidrólisis" in reaction:
        return intro + "Mecanismo: ataque al carbonilo del éster y ruptura del enlace acilo-oxígeno."

    return intro + "Esta combinación todavía requiere una regla más específica."
