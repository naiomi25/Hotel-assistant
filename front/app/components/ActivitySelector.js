import React from "react";
// seleccionamos las actividades
const ActivitySelector = ({
    isActive,
    availableActivities,
    selectedActivities,
    onActivitySelect,
    onConfirm,
    onSkip,
}) => {
    if (!isActive || !availableActivities?.length) return null;

    return (
        <div className="w-full max-w-2xl bg-white p-3 rounded-b-xl border-t border-gray-200 shadow-xl -mt-1 flex flex-col gap-2">
            <p className="text-sm font-medium text-gray-600">Elige tus planes:</p>
            <div className="flex flex-wrap gap-2">
                {availableActivities.map((act, i) => {
                    const selected = selectedActivities?.includes(act);
                    return (
                        <button
                            key={i}
                            onClick={() => onActivitySelect(act)}
                            className={`text-sm px-3 py-1.5 rounded-full font-medium transition-all duration-200 ${selected
                                    ? "bg-emerald-500 text-white scale-[1.02]"
                                    : "bg-blue-100 hover:bg-blue-200 text-blue-700"
                                }`}
                        >
                            {selected ? `✅ ${act}` : act}
                        </button>
                    );
                })}
            </div>

            <div className="flex justify-end space-x-2 pt-2 border-t mt-2 border-gray-100">
                <button
                    onClick={onSkip}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 text-sm px-3 py-1.5 rounded-full"
                >
                    Prefiero no seleccionar nada
                </button>

                <button
                    onClick={onConfirm}
                    disabled={!selectedActivities?.length}
                    className={`text-white text-sm px-4 py-1.5 rounded-full font-semibold ${selectedActivities?.length
                            ? "bg-blue-700 hover:bg-blue-800"
                            : "bg-blue-400 cursor-not-allowed opacity-70"
                        }`}
                >
                    Confirmar Reserva
                </button>
            </div>
        </div>
    );
};

export default ActivitySelector;
