import streamlit as st
import pandas as pd
from collections import Counter
import math
import re

# -------------------- Page Setup --------------------
st.set_page_config(page_title="Word Rank Table — Tidy + Classic", layout="wide")
st.title("Rank of a Word")

# -------------------- Sidebar Info --------------------
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.write(
        """
        This app demonstrates two complementary approaches to calculate 
        the **dictionary rank** of a word (even with repeated letters):

        1. 🧮 *Tidy factorial table* — compact, structured breakdown  
        2. 🧠 *Classic step-by-step logic* — intuitive reasoning with LaTeX math  

        Each step includes:
        - Available letters and their frequencies  
        - Subcases for smaller letters  
        - Factorial expressions rendered in math form
        """
    )
    st.caption("Built for conceptual clarity by ABM(Abhishek Bansal)")

# -------------------- Main Input --------------------
word = st.text_input("🔤 Enter a word:", value="mathematics").strip().upper()

# -------------------- Validation --------------------
if not re.fullmatch(r"[A-Z]+", word):
    st.warning("⚠️ Only A–Z letters allowed.")
elif word:
    letters = list(word)
    unique_sorted = sorted(set(letters))

    # Rank each unique letter
    letter_to_rank = {ch: i + 1 for i, ch in enumerate(unique_sorted)}
    ranks = [letter_to_rank[ch] for ch in letters]

    # Count of smaller letters to the right for each position
    smaller_right = [
        sum(ranks[j] < ranks[i] for j in range(i + 1, len(ranks)))
        for i in range(len(ranks))
    ]

    
    adjusted_factorials = []
    adjusted_values = []
    for i in range(len(letters)):
        r_slice = letters[i:]
        counts = Counter(r_slice)
        num = len(r_slice) - 1

        denom_list = [v for v in counts.values() if v > 1]
        denom_parts = [f"{v}!" for v in denom_list]

        if len(denom_parts) > 1:
            expr = f"{num}! / ({' × '.join(denom_parts)})"
        elif len(denom_parts) == 1:
            expr = f"{num}! / {denom_parts[0]}"
        else:
            expr = f"{num}!"
        adjusted_factorials.append(expr)

        adjusted_values.append(
            math.factorial(num) // math.prod(math.factorial(v) for v in counts.values())
        )

    contributions = [smaller_right[i] * adjusted_values[i] for i in range(len(letters))]
    total_rank = sum(contributions) + 1

    # -------------------- Tidy Factorial Table --------------------
    df = pd.DataFrame(
        [letters, ranks, smaller_right, adjusted_factorials, contributions],
        index=["Letter", "Rank", "Smaller to Right", "Adjusted Factorial", "Contribution"]
    )
    st.markdown("### 📋 Tidy Factorial Table")
    st.dataframe(df, use_container_width=True)

    st.markdown(f"### Rank = **{total_rank}**")
    st.write("""
### ✅ Tidy Method

1. For each position *k*, count how many letters to the right are smaller than the current letter.

2. From position *k* to the end, record the frequencies of all letters (including the letter at *k*).  
   Here:
   - nₖ = total number of letters from position *k* to the end  
   - fⱼ = frequency of the *j*-th distinct letter in that segment  
   These frequencies form the denominator in the adjusted factorial.
""")

    st.latex(r"""
\text{adjusted factorial}(k)
= \frac{(n_k - 1)!}{\prod_j (f_j!)}
""")

    st.write("""
3. Multiply the two quantities to get the contribution at position *k*.

4. Sum all contributions and add 1 to obtain the dictionary rank.

This avoids explicit case-by-case substitution and uses a clean combinatorial multiplier at each position.
""")



    # -------------------- CLASSIC EXPLANATION --------------------
    st.markdown("---")
    st.subheader("🧠 Classic Step-by-Step Logic (Old School Method)")

    total_before = 0

    for i in range(len(letters)):
        current = letters[i]
        right_slice = letters[i:]
        counts = Counter(right_slice)

        smaller_letters = sorted(set(c for c in right_slice if c < current))

        title = (
            f"Step {i+1} — Letter {current} (No Small Letters to the Right)"
            if not smaller_letters
            else f"Step {i+1} — Letter {current} (smaller letters: {', '.join(smaller_letters)})"
        )

        with st.expander(title):
            
            all_letters_desc = "".join(sorted(right_slice))
            st.markdown(
                f"**Position {i+1}:** Current letter is **{current}**.  \n"
                # f"Including this position, available letters: **{all_letters_desc}**."
            )

            counts_remaining_letters = Counter(all_letters_desc)
                
            subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
                
            formatted = []
            for letter in sorted(counts_remaining_letters.keys()):
                    c = counts_remaining_letters[letter]
                    if c > 1:
                        formatted.append(f"{letter}{str(c).translate(subscript_map)}")
                    else:
                        formatted.append(letter)
                
            display_str = " ".join(formatted)
                
            st.markdown(
    f"""
    <div style="font-size: 24px; font-weight: 600;">
        <span style="color: red;">Starting at this letter and extending through all letters to its right: →</span>
        <code>{display_str}</code>
    </div>
    """,
    unsafe_allow_html=True
)    
            

            freq_html = """
            <table style='border-collapse: collapse; font-size: 1.05em;'>
              <tr>
            """
            for ch in sorted(counts.keys()):
                freq_html += (
                    "<th style='padding: 4px 10px; border: 1px solid #ccc; "
                    "color:#1E88E5; font-weight: normal;'>"
                    f"{ch}</th>"
                )
            freq_html += "</tr><tr>"
            for ch in sorted(counts.keys()):
                freq_html += (
                    "<td style='text-align:center; padding: 4px 10px; "
                    "border: 1px solid #ccc;'>"
                    f"{counts[ch]}</td>"
                )
            freq_html += "</tr></table>"
            st.markdown("Frequency Table:", unsafe_allow_html=True)
            st.markdown(freq_html, unsafe_allow_html=True)

            
            common_items = [(ch, counts[ch]) for ch in sorted(counts) if counts[ch] > 1]
            
            common_expr = " × ".join([f"{ch}({v}!)" for ch, v in common_items]) if common_items else "1"
            
            common_fact = " \\times ".join([f"{v}!" for _, v in common_items]) if common_items else "1"
            
            common_value = math.prod(math.factorial(v) for _, v in common_items) if common_items else 1

            if common_value > 1:
                st.markdown("**common_denominator:**")
                st.markdown(f"`{common_expr}`")

            if not smaller_letters:
                st.markdown("No smaller letters to the right → **Contribution = 0.**")
                continue

            # Subcases for each UNIQUE smaller letter
            subtotal = 0
            final_latex_expr = r"\left("
            
            multiplier = 0
            counter_multiplier = 0
            
            for smaller in smaller_letters:
                temp = Counter(right_slice)
                temp[smaller] -= 1
                remaining = len(right_slice) - 1

                # Actual denominator (after placing 'smaller'); keep only freq > 1
                actual_items = [(ch, temp[ch]) for ch in sorted(temp) if temp[ch] > 1]
                actual_expr = " × ".join([f"{ch}({v}!)" for ch, v in actual_items]) if actual_items else "1"
                actual_fact = " \\times ".join([f"{v}!" for _, v in actual_items]) if actual_items else "1"
                actual_value = math.prod(math.factorial(v) for _, v in actual_items) if actual_items else 1

                # Factor = (common denominator) / (actual denominator)
                factor = common_value // actual_value if actual_value else 1

                st.markdown(f"### If **{smaller}** is placed instead of **{current}**:")
                remaining_letters_str = "".join(sorted(temp.elements()))

                # -----------------------------------------
                # Count and format with subscripts
                # -----------------------------------------
                counts_remaining_letters = Counter(remaining_letters_str)
                
                subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
                
                formatted = []
                for letter in sorted(counts_remaining_letters.keys()):
                    c = counts_remaining_letters[letter]
                    if c > 1:
                        formatted.append(f"{letter}{str(c).translate(subscript_map)}")
                    else:
                        formatted.append(letter)
                
                display_str = " ".join(formatted)
                
                # -----------------------------------------
                # Display enlarged in Streamlit
                # -----------------------------------------
                st.markdown(
    f"""
    <div style="font-size: 24px; font-weight: 600;">
        <span style="color: blue;">Remaining letters →</span>
        <code>{display_str}</code>
    </div>
    """,
    unsafe_allow_html=True
)

            
                count = factor * (math.factorial(remaining) // (common_value if common_value else 1))
                
                
                if factor > 1:
                    multiplier += factor
                    counter_multiplier += 1
                    if actual_value > 1:
                        latex_expr = (
                        f"{factor} \\times \\frac{{{remaining}!}}{{{common_fact}}} = "
                        f"\\frac{{{remaining}!}}{{{actual_fact}}} = "
                        f"{count}"
                        )
                        final_latex_expr += f"{factor}+"
                    else:
                        latex_expr = (
                        f"{factor} \\times \\frac{{{remaining}!}}{{{common_fact}}} = "
                        f"{remaining}! = "
                        f"{count}"
                        )
                        final_latex_expr += f"{factor}+"    
                else:
                    multiplier += 1
                    counter_multiplier += 1
                    if actual_value > 1:
                        latex_expr = (
                        f"\\frac{{{remaining}!}}{{{actual_fact}}} = "
                        f"{count}"
                        )
                        final_latex_expr += f"{factor}+"
                    else:
                        latex_expr = (
                        f"{remaining}! = "
                        f"{count}"
                        )
                        final_latex_expr += f"{factor}+"
                st.latex(latex_expr)
                subtotal += count

            if final_latex_expr.endswith("+"):
                final_latex_expr = final_latex_expr[:-1]
            if counter_multiplier == 1:
                if final_latex_expr.startswith("\left("):
                        final_latex_expr = final_latex_expr[7:]
                if multiplier == 1:
                    if common_value > 1:
                        
                        final_latex_expr += fr"\frac{{{remaining}!}}{{{common_fact}}} = "
                        final_latex_expr += fr"{subtotal}"
                    else:
                        
                        final_latex_expr += fr"{remaining}! = "
                        final_latex_expr += fr"{subtotal}"
                else:
                    if common_value > 1:
                        
                        final_latex_expr += fr"{multiplier} \times \frac{{{remaining}!}}{{{common_fact}}} = "
                        final_latex_expr += fr"{subtotal}"
                        
                    else:
                        
                        final_latex_expr += fr"{remaining}! = "
                        final_latex_expr += fr"{subtotal}"
                    
            else:
                if common_value > 1:
                    final_latex_expr += fr"\right) \times \frac{{{remaining}!}}{{{common_fact}}} = "
                    final_latex_expr += fr"{multiplier} \times \frac{{{remaining}!}}{{{common_fact}}} = "
                    final_latex_expr += fr"{subtotal}"
                else:
                    final_latex_expr += fr"\right) \times {remaining}! = "
                    final_latex_expr += fr"{multiplier} \times {remaining}! = "
                    final_latex_expr += fr"{subtotal}"   

            st.markdown(
    """
    <div style="text-align:center;">
        <hr style="
            width:40%;
            margin-top:20px;
            margin-bottom:20px;
            border:0;
            border-top:1px solid #d1d5db;
        ">
    </div>
    """,
    unsafe_allow_html=True
)


            st.latex(final_latex_expr)

            st.markdown(
    f"""
    <div style="
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid rgba(200, 200, 200, 0.45);
        padding: 16px 22px;
        margin: 18px 0;
        border-radius: 14px;
        font-size: 22px;
        font-weight: 300;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display',
                     'Segoe UI', Roboto, sans-serif;
        color: #1c1c1e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        Subtotal contribution at position {i+1}: {subtotal} words
    </div>
    """,
    unsafe_allow_html=True
)




            total_before += subtotal

    # -------------------- Final Rank Summary --------------------
    st.markdown(f"### ➕ Total words before **{word}** = **{total_before}**")
    st.markdown(f"### Rank = **{total_before + 1}**")

else:
    st.info("Enter a word above to see its rank table and detailed explanation.")
