import customtkinter as ctk
import requests
from tkinter import messagebox
from PIL import Image
from io import BytesIO
import webbrowser
# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
API_KEY = "YOUR_API_KEY"  # your key
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
RECIPE_INFO_URL = "https://api.spoonacular.com/recipes/{id}/information"

# ------------------------------------------------------------
# APP
# ------------------------------------------------------------
class RecipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍳 Smart Recipe Finder (Live Data)")
        self.geometry("950x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")  # You can replace with "purple.json"

        # ---------------- Title ----------------
        title_label = ctk.CTkLabel(
            self,
            text="🍽 Smart Recipe Finder",
            font=("Segoe UI", 28, "bold")
        )
        title_label.pack(pady=15)

        # ---------------- Input Frame ----------------
        input_frame = ctk.CTkFrame(self, corner_radius=10)
        input_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(
            input_frame,
            text="Enter ingredients (comma-separated):",
            font=("Segoe UI", 14)
        ).pack(side="left", padx=10)

        self.entry = ctk.CTkEntry(
            input_frame,
            width=400,
            font=("Segoe UI", 14),
            placeholder_text="e.g. bread, garlic, onion, chicken"
        )
        self.entry.pack(side="left", padx=10)

        search_button = ctk.CTkButton(
            input_frame,
            text="🔍 Find Recipes",
            font=("Segoe UI", 14, "bold"),
            fg_color="#2FA572",
            hover_color="#218A5B",
            command=self.find_recipes
        )
        search_button.pack(side="left", padx=10)

        # ---------------- Results Scroll Area ----------------
        self.results_frame = ctk.CTkScrollableFrame(self, width=850, height=500)
        self.results_frame.pack(pady=20)

    # --------------------------------------------------------
    # FETCH RECIPES
    # --------------------------------------------------------
    def find_recipes(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        ingredients = self.entry.get().strip()
        if not ingredients:
            messagebox.showwarning("Input Required", "Please enter ingredients.")
            return
        params = {
            "apiKey": API_KEY,
            "ingredients": ingredients,
            "number": 10,
            "ranking": 1,
            "ignorePantry": True
        }
        try:
            loading_label = ctk.CTkLabel(
                self.results_frame,
                text="Fetching live recipes...",
                font=("Segoe UI", 14)
            )
            loading_label.pack(pady=20)
            self.update_idletasks()

            resp = requests.get(API_URL, params=params)
            if resp.status_code != 200:
                messagebox.showerror("API Error", resp.text)
                return

            data = resp.json()
            loading_label.destroy()

            if not data:
                ctk.CTkLabel(
                    self.results_frame,
                    text="❌ No recipes found. Try more ingredients.",
                    font=("Segoe UI", 14)
                ).pack(pady=20)
                return

            for recipe in data:
                self.display_recipe(recipe)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --------------------------------------------------------
    # RECIPE BLOCK
    # --------------------------------------------------------
    def display_recipe(self, recipe):
        frame = ctk.CTkFrame(self.results_frame, corner_radius=10)
        frame.pack(fill="x", pady=10, padx=10)

        title = recipe.get("title", "Unnamed Recipe")

        ctk.CTkLabel(
            frame,
            text=f"🍴 {title}",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=5)

        # ------- IMAGE -------
        image_url = recipe.get("image")
        if image_url:
            try:
                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data)).resize((150, 150))
                tk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
                ctk.CTkLabel(content_frame, image=tk_img, text="").pack(side="left", padx=15)
            except:
                pass

        # ------- INGREDIENTS -------
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10)

        used = [i["name"] for i in recipe.get("usedIngredients", [])]
        missed = [i["name"] for i in recipe.get("missedIngredients", [])]

        text = f"✅ Used: {', '.join(used)}\n"
        if missed:
            text += f"⚠ Missing: {', '.join(missed)}\n"
        text += f"Recipe ID: {recipe.get('id')}"

        ctk.CTkLabel(
            info_frame,
            text=text,
            justify="left",
            wraplength=650,
            font=("Consolas", 12)
        ).pack(anchor="w")

        # ------- BUTTON -------
        ctk.CTkButton(
            frame,
            text="Get Recipe",
            fg_color="#2FA572",
            hover_color="#1E7D56",
            command=lambda rid=recipe.get("id"): self.show_recipe_details(rid)
        ).pack(anchor="e", padx=20, pady=10)
    # --------------------------------------------------------
    # POPUP RECIPE DETAILS
    # --------------------------------------------------------
    def show_recipe_details(self, recipe_id):
        try:
            resp = requests.get(RECIPE_INFO_URL.format(id=recipe_id),
                                params={"apiKey": API_KEY})

            if resp.status_code != 200:
                messagebox.showerror("API Error", resp.text)
                return

            details = resp.json()

            popup = ctk.CTkToplevel(self)
            popup.title(details.get("title", "Recipe Details"))
            popup.geometry("700x600")

            ctk.CTkLabel(
                popup,
                text=details.get("title", "Recipe Details"),
                font=("Segoe UI", 20, "bold")
            ).pack(pady=10)

            # IMAGE
            img_url = details.get("image")
            if img_url:
                try:
                    img_data = requests.get(img_url).content
                    img = Image.open(BytesIO(img_data)).resize((250, 250))
                    tk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))
                    ctk.CTkLabel(popup, image=tk_img, text="").pack(pady=10)
                except:
                    pass

            # SUMMARY
            summary = details.get("summary", "No description.").replace("<b>", "").replace("</b>", "")
            summary = summary.replace("<a", "").replace("</a>", "")

            ctk.CTkLabel(
                popup,
                text=summary,
                justify="left",
                wraplength=600,
                font=("Segoe UI", 12)
            ).pack(pady=10)

            # LINK BUTTON
            if details.get("sourceUrl"):
                ctk.CTkButton(
                    popup,
                    text="View Full Recipe Online",
                    fg_color="#2FA572",
                    hover_color="#1E7D56",
                    command=lambda: webbrowser.open(details["sourceUrl"])
                ).pack(pady=15)

        except Exception as e:
            messagebox.showerror("Error", str(e))


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()