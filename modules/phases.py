PHASES = {
    'J5': [
        {
            "primary":  "srrrGGrrrrsrrrGGrrrrr",
            "yellow":   "srrryyrrrrsrrryyrrrrr",
            "red":      "srrrrrrrrrsrrrrrrrrrr"
        },
        {
            "primary":  "GGGGrrsrrrGGGGrrsrrrr",
            "yellow":   "yyyyrrsrrryyyyrrsrrrr",
            "red":      "srrrrrsrrrsrrrrrrrrrr"
        },
        {
            "primary":  "srrrrrGGggsrrrrrGGggr",
            "yellow":   "srrrrryyyysrrrrryyyyr",
            "red":      "srrrrrrrrrsrrrrrrrrrr"
        }
    ],

    'J4': [
        {
            "primary":  "srrrGGsrrrrrsrrrGGsrrrrr",
            "yellow":   "srrryysrrrrrsrrryysrrrrr",
            "red":      "srrrrrrrrrrrsrrrrrsrrrrr"
        },
        {
            "primary":  "GGGGrrsrrrrrGGGGrrsrrrrr",
            "yellow":   "yyyyrrsrrrrryyyyrrsrrrrr",
            "red":      "srrrrrsrrrrrsrrrrrsrrrrr"
        },
        {
            "primary":  "srrrrrrrrGGGsrrrrrrrrGGG",
            "yellow":   "srrrrrrrryyysrrrrrrrryyy",
            "red":      "srrrrrrrrrrrsrrrrrrrrrrr"
        },
        {
            "primary":  "srrrrrGGGrrrsrrrrrGGGrrr",
            "yellow":   "srrrrryyyrrrsrrrrryyyrrr",
            "red":      "srrrrrrrrrrrsrrrrrrrrrrr"
        }

    ],

    'J3': [
        {
            "primary":  "srrrGGsrrrsrrrGGrrrrr",
            "yellow":   "srrryysrrrsrrryyrrrrr",
            "red":      "srrrrrrrrrsrrrrrrrrrr"
        },
        {
            "primary":  "GGGGrrsrrrGGGGrrsrrrr",
            "yellow":   "yyyyrrsrrryyyyrrsrrrr",
            "red":      "srrrrrsrrrrrrrrrsrrrr"
        },
        {
            "primary":  "srrrrrGGggrrrrrrGGggr",
            "yellow":   "srrrrryyyyrrrrrryyyyr",
            "red":      "srrrrrrrrrrrrrrrrrrrr"
        },{
            "primary":  "srrrGGsrrrsrrrGGrrrrr",
            "yellow":   "srrryysrrrsrrryyrrrrr",
            "red":      "srrrrrrrrrsrrrrrrrrrr"
        }
    ],

    'J2': [
        {
                "primary":  "srrrsrrrGGsrrrsrrrrGG",
                "yellow":   "srrrsrrryysrrrsrrrryy",
                "red":      "srrrsrrrrrrrrrsrrrrrr"
        },
        {
            "primary":  "srrrGGGGrrsrrrGGGGGrr",
            "yellow":   "srrryyyyrrsrrryyyyyrr",
            "red":      "srrrsrrrrrsrrrsrrrrrr"
        },
        {
            "primary":  "srGGsrrrrrsrGGsrrrrrr",
            "yellow":   "sryysrrrrrsryysrrrrrr",
            "red":      "srrrsrrrrrsrrrsrrrrrr"
        },
        {
            "primary":  "GGrrsrrrrrGGrrsrrrrrr",
            "yellow":   "yyrrsrrrrryyrrsrrrrrr",
            "red":      "rrrrsrrrrrrrrrsrrrrrr"
        }
    ],

    'J1': [
        {
            "primary":  "srrrGGsrrrsrrrGGGsrrrr",
            "yellow":   "srrryysrrrsrrryyysrrrr",
            "red":      "srrrrrsrrrsrrrrrrsrrrr"
        },
        {
            "primary":  "GGGGrrsrrrGGGGrrrsrrrr",
            "yellow":   "yyyyrrsrrryyyyrrrsrrrr",
            "red":      "srrrrrsrrrsrrrrrrsrrrr"
        },
        {
            "primary":  "srrrrrsrGGsrrrrrrsrGGG",
            "yellow":   "srrrrrsryysrrrrrrsryyy",
            "red":      "srrrrrrrrrsrrrrrrsrrrr"
        },
        {
            "primary":  "srrrrrGGrrsrrrrrrGGrrr",
            "yellow":   "srrrrryyrrsrrrrrryyrrr",
            "red":      "srrrrrrrrrsrrrrrrrrrrr"
        }
    ]
}

def get_phases(junction):
    return PHASES[junction]
