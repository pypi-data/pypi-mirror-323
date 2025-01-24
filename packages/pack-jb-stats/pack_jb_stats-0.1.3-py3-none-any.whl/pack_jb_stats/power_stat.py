import math
import scipy.stats as stats

# Définition de la fonction de calcul
def power_stat(effect_size, control_group_rate, proportion_treated, alpha):
    power = 0.8
    effect_size = effect_size / 100
    base1 = ((effect_size + control_group_rate) * (1 - (effect_size + control_group_rate)) / proportion_treated)
    base2 = (control_group_rate * (1 - control_group_rate) / (1 - proportion_treated))
    
    full_base = base1 + base2
    
    alpha_2 = stats.norm.ppf(alpha / 2)
    power_2 = stats.norm.ppf(1 - power)
    
    normal_term = (alpha_2 + power_2) ** 2
    
    result = full_base * normal_term * (1 / (effect_size ** 2))
    
    sample_size_control = result * (1 - proportion_treated)
    sample_size_treated = result * proportion_treated
    
    result = math.ceil(result)
    sample_size_treated = math.ceil(sample_size_treated)
    sample_size_control = math.ceil(sample_size_control)
    
    return result, sample_size_control, sample_size_treated

# Définition de la fonction principale
def power():
    try:
        effect_size = float(input("Veuillez entrer la taille de l'impact attendu (impact de deux points -> 2) : "))
        control_group_rate = float(input("Veuillez entrer le niveau de base de l'indicateur de résultat : "))
        proportion_treated = float(input("Veuillez entrer la part de la population totale que vous souhaitez traiter : "))
        alpha = float(input("Veuillez entrer le niveau de significativité (95% -> 0.05, 90% -> 0.1): "))
        
        # Appeler la fonction avec les valeurs fournies
        result, sample_size_control, sample_size_treated = power_stat(effect_size, control_group_rate, proportion_treated, alpha)
        
        print()
        print(f"La taille totale de l'échantillon nécessaire est : {result} observations")
        print(f"Avec une taille du groupe contrôle de : {sample_size_control} observations")
        print(f"Avec une taille du groupe traité de : {sample_size_treated} observations")
    
    except ValueError:
        print("Veuillez entrer des valeurs numériques valides.")


def smd_plot(df, group_col, variables, threshold=0.03):
    diff_dict = {}

    # Separate treated and control groups based on the grouping column
    treated = df[df[group_col] == 1.0]
    control = df[df[group_col] == 0.0]
    
    # Calculate the absolute differences for each category of each variable
    for var in variables:
        category_diffs = {}
        categories = df[var].unique()  # Get unique categories
        
        # Iterate over categories to calculate differences for each category
        for category in categories:
            # Proportions for the current category in treated and control groups
            p_treated = treated[var].value_counts(normalize=True).get(category, 0)
            p_control = control[var].value_counts(normalize=True).get(category, 0)
            
            # Calculate the absolute difference between the proportions for this category
            diff = abs(p_treated - p_control)
            category_diffs[category] = diff
        
        diff_dict[var] = category_diffs
    
    # Convert the results to a DataFrame for easy plotting
    diff_data = []
    for var, categories in diff_dict.items():
        for category, diff in categories.items():
            diff_data.append([var, str(category), diff])
    
    diff_df = pd.DataFrame(diff_data, columns=['Variable', 'Category', 'Difference'])

    # Plotting the differences as dots for each category of each variable
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Difference', y='Category', hue='Variable', data=diff_df, palette='Set2', s=25, marker='x')

    # Add a vertical line for the threshold
    plt.axvline(x=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold = {threshold}')

    # Add some aesthetics for the plot
    plt.title("Absolute Differences in Category Proportions between Treated and Control Groups")
    plt.xlabel("Absolute Difference in Proportion (Treated - Control)")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.legend(title="Variable", loc='upper right')
    plt.show()


