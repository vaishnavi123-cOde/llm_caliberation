import random
import json
import os
from typing import List, Dict


QUESTIONS_DATA = [
    # Science
    {"question": "What is the chemical symbol for gold?", "options": ["Au", "Ag", "Fe", "Cu"], "answer": "Au", "category": "Science"},
    {"question": "What planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "answer": "Mars", "category": "Science"},
    {"question": "What is the speed of light in vacuum (m/s)?", "options": ["3 x 10^8", "3 x 10^6", "3 x 10^10", "3 x 10^12"], "answer": "3 x 10^8", "category": "Science"},
    {"question": "What is the powerhouse of the cell?", "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus"], "answer": "Mitochondria", "category": "Science"},
    {"question": "What gas do plants absorb from the atmosphere?", "options": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], "answer": "Carbon dioxide", "category": "Science"},
    {"question": "What is the atomic number of carbon?", "options": ["4", "6", "8", "12"], "answer": "6", "category": "Science"},
    {"question": "What force keeps planets in orbit around the sun?", "options": ["Electromagnetic", "Gravity", "Strong nuclear", "Weak nuclear"], "answer": "Gravity", "category": "Science"},
    {"question": "What is the hardest natural substance?", "options": ["Gold", "Iron", "Diamond", "Platinum"], "answer": "Diamond", "category": "Science"},
    {"question": "What is the boiling point of water at sea level in Celsius?", "options": ["90", "100", "110", "120"], "answer": "100", "category": "Science"},
    {"question": "Which blood type is the universal donor?", "options": ["A", "B", "AB", "O"], "answer": "O", "category": "Science"},
    {"question": "What is the largest organ in the human body?", "options": ["Liver", "Brain", "Skin", "Heart"], "answer": "Skin", "category": "Science"},
    {"question": "What particle has a negative charge?", "options": ["Proton", "Neutron", "Electron", "Positron"], "answer": "Electron", "category": "Science"},
    {"question": "What is the pH of pure water?", "options": ["5", "7", "9", "11"], "answer": "7", "category": "Science"},
    {"question": "Which vitamin is produced when skin is exposed to sunlight?", "options": ["Vitamin A", "Vitamin B", "Vitamin C", "Vitamin D"], "answer": "Vitamin D", "category": "Science"},
    {"question": "What element is needed for combustion?", "options": ["Nitrogen", "Oxygen", "Hydrogen", "Carbon"], "answer": "Oxygen", "category": "Science"},
    {"question": "What is the SI unit of force?", "options": ["Joule", "Newton", "Watt", "Pascal"], "answer": "Newton", "category": "Science"},
    {"question": "What galaxy is Earth in?", "options": ["Andromeda", "Milky Way", "Triangulum", "Sombrero"], "answer": "Milky Way", "category": "Science"},
    {"question": "What is the most abundant gas in Earth's atmosphere?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Argon"], "answer": "Nitrogen", "category": "Science"},
    {"question": "What is the process by which plants make food?", "options": ["Respiration", "Photosynthesis", "Fermentation", "Digestion"], "answer": "Photosynthesis", "category": "Science"},
    {"question": "What is the smallest unit of matter?", "options": ["Molecule", "Atom", "Cell", "Electron"], "answer": "Atom", "category": "Science"},
    {"question": "What type of bond involves sharing electrons?", "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "answer": "Covalent", "category": "Science"},
    {"question": "What is the main function of red blood cells?", "options": ["Fight infection", "Carry oxygen", "Clot blood", "Produce hormones"], "answer": "Carry oxygen", "category": "Science"},
    {"question": "What is the freezing point of water in Celsius?", "options": ["-10", "0", "10", "32"], "answer": "0", "category": "Science"},
    {"question": "Which planet has the most moons?", "options": ["Jupiter", "Saturn", "Uranus", "Neptune"], "answer": "Saturn", "category": "Science"},
    {"question": "What is the chemical formula for water?", "options": ["H2O", "CO2", "NaCl", "HCl"], "answer": "H2O", "category": "Science"},
    {"question": "What is the unit of electrical resistance?", "options": ["Volt", "Ampere", "Ohm", "Farad"], "answer": "Ohm", "category": "Science"},
    {"question": "What type of rock is formed from cooled magma?", "options": ["Sedimentary", "Igneous", "Metamorphic", "Fossilized"], "answer": "Igneous", "category": "Science"},
    {"question": "What is the largest planet in our solar system?", "options": ["Saturn", "Jupiter", "Neptune", "Uranus"], "answer": "Jupiter", "category": "Science"},
    {"question": "What is the chemical formula for table salt?", "options": ["KCl", "NaCl", "CaCl2", "MgCl2"], "answer": "NaCl", "category": "Science"},
    {"question": "What is the human body's largest artery?", "options": ["Pulmonary", "Aorta", "Carotid", "Femoral"], "answer": "Aorta", "category": "Science"},
    {"question": "How many bones are in the adult human body?", "options": ["106", "206", "306", "406"], "answer": "206", "category": "Science"},
    {"question": "What element has the symbol 'Fe'?", "options": ["Francium", "Iron", "Fermium", "Fluorine"], "answer": "Iron", "category": "Science"},
    {"question": "What is the main gas found in the Sun?", "options": ["Helium", "Hydrogen", "Oxygen", "Carbon"], "answer": "Hydrogen", "category": "Science"},
    {"question": "What is the process by which liquid turns to gas?", "options": ["Condensation", "Evaporation", "Sublimation", "Deposition"], "answer": "Evaporation", "category": "Science"},
    {"question": "What is the unit of frequency?", "options": ["Hertz", "Decibel", "Lumen", "Tesla"], "answer": "Hertz", "category": "Science"},
    {"question": "What is the largest internal organ in the human body?", "options": ["Heart", "Liver", "Brain", "Lungs"], "answer": "Liver", "category": "Science"},
    {"question": "What planet is closest to the sun?", "options": ["Venus", "Mercury", "Earth", "Mars"], "answer": "Mercury", "category": "Science"},
    {"question": "What is the term for animals that eat only plants?", "options": ["Carnivores", "Herbivores", "Omnivores", "Detritivores"], "answer": "Herbivores", "category": "Science"},
    {"question": "What is the speed of sound in air roughly (m/s)?", "options": ["150", "343", "700", "1000"], "answer": "343", "category": "Science"},
    {"question": "What is the DNA shape called?", "options": ["Alpha helix", "Double helix", "Beta sheet", "Single strand"], "answer": "Double helix", "category": "Science"},
    {"question": "Which planet rotates on its side?", "options": ["Uranus", "Neptune", "Pluto", "Saturn"], "answer": "Uranus", "category": "Science"},
    {"question": "What type of energy is stored in a battery?", "options": ["Kinetic", "Thermal", "Chemical", "Nuclear"], "answer": "Chemical", "category": "Science"},
    {"question": "What is the largest moon of Saturn?", "options": ["Europa", "Ganymede", "Titan", "Callisto"], "answer": "Titan", "category": "Science"},
    {"question": "What is the main type of bond in a water molecule?", "options": ["Ionic", "Covalent", "Hydrogen", "Metallic"], "answer": "Covalent", "category": "Science"},
    {"question": "What is the function of the nervous system?", "options": ["Digestion", "Signal transmission", "Circulation", "Respiration"], "answer": "Signal transmission", "category": "Science"},
    {"question": "What is the chemical symbol for sodium?", "options": ["So", "Sd", "Na", "Nd"], "answer": "Na", "category": "Science"},
    {"question": "What is the smallest planet in our solar system?", "options": ["Mars", "Mercury", "Venus", "Pluto"], "answer": "Mercury", "category": "Science"},
    {"question": "What is the term for a species' natural home?", "options": ["Biome", "Ecosystem", "Habitat", "Niche"], "answer": "Habitat", "category": "Science"},
    {"question": "What is the unit of electric current?", "options": ["Volt", "Ohm", "Ampere", "Watt"], "answer": "Ampere", "category": "Science"},
    {"question": "What is the most abundant element in the universe?", "options": ["Helium", "Hydrogen", "Oxygen", "Carbon"], "answer": "Hydrogen", "category": "Science"},
    {"question": "What type of lens is thicker at the center?", "options": ["Concave", "Convex", "Plano", "Cylindrical"], "answer": "Convex", "category": "Science"},
    {"question": "What is the main pigment in plants?", "options": ["Carotene", "Xanthophyll", "Chlorophyll", "Melanin"], "answer": "Chlorophyll", "category": "Science"},
    {"question": "How many chromosomes do humans have?", "options": ["23", "44", "46", "48"], "answer": "46", "category": "Science"},
    {"question": "What is the study of fungi called?", "options": ["Botany", "Mycology", "Virology", "Bacteriology"], "answer": "Mycology", "category": "Science"},
    {"question": "What is the SI unit of energy?", "options": ["Newton", "Joule", "Watt", "Pascal"], "answer": "Joule", "category": "Science"},
    {"question": "What element is liquid at room temperature?", "options": ["Mercury", "Iron", "Gold", "Lead"], "answer": "Mercury", "category": "Science"},
    {"question": "What is the process of cell division in somatic cells?", "options": ["Meiosis", "Mitosis", "Fission", "Budding"], "answer": "Mitosis", "category": "Science"},
    {"question": "What is the main source of energy for Earth?", "options": ["Moon", "Sun", "Geothermal", "Nuclear"], "answer": "Sun", "category": "Science"},
    {"question": "What is the term for a substance that speeds up a reaction?", "options": ["Reactant", "Product", "Catalyst", "Inhibitor"], "answer": "Catalyst", "category": "Science"},
    {"question": "What is the chemical symbol for potassium?", "options": ["Po", "Pt", "K", "P"], "answer": "K", "category": "Science"},
    {"question": "What is the largest type of blood vessel?", "options": ["Capillary", "Vein", "Artery", "Venule"], "answer": "Artery", "category": "Science"},
    {"question": "What is the study of earthquakes called?", "options": ["Geology", "Seismology", "Meteorology", "Volcanology"], "answer": "Seismology", "category": "Science"},
    {"question": "What is the name of the galaxy closest to the Milky Way?", "options": ["Sombrero", "Andromeda", "Triangulum", "Whirlpool"], "answer": "Andromeda", "category": "Science"},
    {"question": "What particle has no charge?", "options": ["Proton", "Electron", "Neutron", "Positron"], "answer": "Neutron", "category": "Science"},
    {"question": "What is the human body's longest bone?", "options": ["Tibia", "Fibula", "Femur", "Humerus"], "answer": "Femur", "category": "Science"},
    {"question": "What type of bond involves electron transfer?", "options": ["Covalent", "Metallic", "Ionic", "Hydrogen"], "answer": "Ionic", "category": "Science"},
    {"question": "What element is used in light bulbs?", "options": ["Copper", "Tungsten", "Silver", "Aluminum"], "answer": "Tungsten", "category": "Science"},
    {"question": "What is the main component of the Sun?", "options": ["Helium", "Hydrogen", "Carbon", "Iron"], "answer": "Hydrogen", "category": "Science"},
    {"question": "What is the normal human body temperature in Celsius?", "options": ["35.0", "36.5", "37.0", "38.0"], "answer": "37.0", "category": "Science"},
    {"question": "What is the outermost layer of Earth called?", "options": ["Mantle", "Core", "Crust", "Lithosphere"], "answer": "Crust", "category": "Science"},
    {"question": "What is the study of heredity called?", "options": ["Genetics", "Biology", "Evolution", "Ecology"], "answer": "Genetics", "category": "Science"},
    {"question": "What planet has the Great Red Spot?", "options": ["Mars", "Saturn", "Jupiter", "Neptune"], "answer": "Jupiter", "category": "Science"},
    {"question": "What is the main type of rock found on the ocean floor?", "options": ["Granite", "Basalt", "Limestone", "Sandstone"], "answer": "Basalt", "category": "Science"},

    # History
    {"question": "In what year did World War II end?", "options": ["1943", "1944", "1945", "1946"], "answer": "1945", "category": "History"},
    {"question": "Who was the first President of the United States?", "options": ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"], "answer": "George Washington", "category": "History"},
    {"question": "What ancient civilization built the pyramids?", "options": ["Roman", "Greek", "Egyptian", "Mesopotamian"], "answer": "Egyptian", "category": "History"},
    {"question": "What year did the Berlin Wall fall?", "options": ["1987", "1988", "1989", "1990"], "answer": "1989", "category": "History"},
    {"question": "Who discovered America in 1492?", "options": ["Vasco da Gama", "Ferdinand Magellan", "Christopher Columbus", "Amerigo Vespucci"], "answer": "Christopher Columbus", "category": "History"},
    {"question": "What empire was ruled by Genghis Khan?", "options": ["Ottoman", "Roman", "Mongol", "Persian"], "answer": "Mongol", "category": "History"},
    {"question": "What was the Renaissance a revival of?", "options": ["Science", "Art and learning", "Religion", "Warfare"], "answer": "Art and learning", "category": "History"},
    {"question": "Who painted the Mona Lisa?", "options": ["Michelangelo", "Raphael", "Leonardo da Vinci", "Donatello"], "answer": "Leonardo da Vinci", "category": "History"},
    {"question": "What country built the first atomic bomb?", "options": ["Germany", "Soviet Union", "United States", "United Kingdom"], "answer": "United States", "category": "History"},
    {"question": "Which war was fought between the North and South in the US?", "options": ["Revolutionary War", "Civil War", "War of 1812", "World War I"], "answer": "Civil War", "category": "History"},
    {"question": "What was the name of the first manned moon landing mission?", "options": ["Apollo 11", "Apollo 13", "Gemini 4", "Mercury 9"], "answer": "Apollo 11", "category": "History"},
    {"question": "Who was the first woman to fly solo across the Atlantic?", "options": ["Amelia Earhart", "Harriet Quimby", "Bessie Coleman", "Jacqueline Cochran"], "answer": "Amelia Earhart", "category": "History"},
    {"question": "What ancient wonder was located in Babylon?", "options": ["Colossus", "Hanging Gardens", "Great Pyramid", "Lighthouse"], "answer": "Hanging Gardens", "category": "History"},
    {"question": "What year did the Titanic sink?", "options": ["1910", "1911", "1912", "1913"], "answer": "1912", "category": "History"},
    {"question": "Who led the Indian independence movement?", "options": ["Jawaharlal Nehru", "Mahatma Gandhi", "Subhas Chandra Bose", "Bhagat Singh"], "answer": "Mahatma Gandhi", "category": "History"},
    {"question": "What wall divided Berlin?", "options": ["Great Wall", "Hadrian's Wall", "Berlin Wall", "Western Wall"], "answer": "Berlin Wall", "category": "History"},
    {"question": "What dynasty built the Forbidden City?", "options": ["Tang", "Song", "Ming", "Qing"], "answer": "Ming", "category": "History"},
    {"question": "Who was the last Pharaoh of Egypt?", "options": ["Nefertiti", "Hatshepsut", "Cleopatra", "Ramesses"], "answer": "Cleopatra", "category": "History"},
    {"question": "What event started World War I?", "options": ["Sinking of Lusitania", "Assassination of Archduke Ferdinand", "Invasion of Poland", "Battle of the Somme"], "answer": "Assassination of Archduke Ferdinand", "category": "History"},
    {"question": "Who wrote the Declaration of Independence?", "options": ["George Washington", "Benjamin Franklin", "Thomas Jefferson", "John Adams"], "answer": "Thomas Jefferson", "category": "History"},
    {"question": "What was the longest war in history?", "options": ["Hundred Years' War", "Vietnam War", "Thirty Years' War", "Peloponnesian War"], "answer": "Hundred Years' War", "category": "History"},
    {"question": "What country gave the Statue of Liberty to the US?", "options": ["Spain", "France", "United Kingdom", "Italy"], "answer": "France", "category": "History"},
    {"question": "What ship brought the Pilgrims to America?", "options": ["Santa Maria", "Mayflower", "Beagle", "Victoria"], "answer": "Mayflower", "category": "History"},
    {"question": "What year did the Soviet Union collapse?", "options": ["1989", "1990", "1991", "1992"], "answer": "1991", "category": "History"},
    {"question": "Who was the first Emperor of Rome?", "options": ["Julius Caesar", "Augustus", "Nero", "Caligula"], "answer": "Augustus", "category": "History"},
    {"question": "What was the name of the ship that brought Darwin to the Galapagos?", "options": ["Victory", "Beagle", "Endeavour", "Discovery"], "answer": "Beagle", "category": "History"},
    {"question": "What treaty ended World War I?", "options": ["Treaty of Paris", "Treaty of Versailles", "Treaty of Ghent", "Treaty of Westphalia"], "answer": "Treaty of Versailles", "category": "History"},
    {"question": "What country was divided at the 38th parallel?", "options": ["Germany", "Vietnam", "Korea", "India"], "answer": "Korea", "category": "History"},
    {"question": "Who invented the printing press?", "options": ["Benjamin Franklin", "Johannes Gutenberg", "Thomas Edison", "Galileo Galilei"], "answer": "Johannes Gutenberg", "category": "History"},
    {"question": "What empire did the Aztecs belong to?", "options": ["Inca", "Maya", "Mexica", "Olmec"], "answer": "Mexica", "category": "History"},
    {"question": "What was the name of the US program to put a man on the moon?", "options": ["Mercury", "Gemini", "Apollo", "Artemis"], "answer": "Apollo", "category": "History"},
    {"question": "Who wrote the 'I Have a Dream' speech?", "options": ["Malcolm X", "Martin Luther King Jr.", "John F. Kennedy", "Frederick Douglass"], "answer": "Martin Luther King Jr.", "category": "History"},
    {"question": "What year did the French Revolution begin?", "options": ["1776", "1789", "1799", "1804"], "answer": "1789", "category": "History"},
    {"question": "Who was the first European to reach India by sea?", "options": ["Columbus", "Vasco da Gama", "Magellan", "Drake"], "answer": "Vasco da Gama", "category": "History"},

    # Mathematics
    {"question": "What is the square root of 144?", "options": ["10", "11", "12", "13"], "answer": "12", "category": "Mathematics"},
    {"question": "What is the value of pi to two decimal places?", "options": ["3.14", "3.15", "3.16", "3.13"], "answer": "3.14", "category": "Mathematics"},
    {"question": "What is 7 x 8?", "options": ["54", "56", "58", "64"], "answer": "56", "category": "Mathematics"},
    {"question": "What is the derivative of x^2?", "options": ["x", "2x", "x^2", "2"], "answer": "2x", "category": "Mathematics"},
    {"question": "What is the integral of 1/x?", "options": ["ln(x)", "e^x", "x", "1"], "answer": "ln(x)", "category": "Mathematics"},
    {"question": "What is the area of a circle with radius 5?", "options": ["25π", "10π", "5π", "15π"], "answer": "25π", "category": "Mathematics"},
    {"question": "What is 15% of 200?", "options": ["15", "20", "30", "35"], "answer": "30", "category": "Mathematics"},
    {"question": "What is the value of 2^10?", "options": ["512", "1024", "2048", "256"], "answer": "1024", "category": "Mathematics"},
    {"question": "What is the factorial of 5?", "options": ["60", "120", "24", "100"], "answer": "120", "category": "Mathematics"},
    {"question": "What is the sum of angles in a triangle (degrees)?", "options": ["90", "180", "270", "360"], "answer": "180", "category": "Mathematics"},
    {"question": "What is the next prime number after 7?", "options": ["8", "9", "10", "11"], "answer": "11", "category": "Mathematics"},
    {"question": "What is the logarithm base 10 of 100?", "options": ["1", "2", "3", "10"], "answer": "2", "category": "Mathematics"},
    {"question": "What is the Pythagorean theorem formula?", "options": ["a^2 + b^2 = c^2", "a + b = c", "a^2 = b^2 + c^2", "a * b = c"], "answer": "a^2 + b^2 = c^2", "category": "Mathematics"},
    {"question": "What is the slope of y = 3x + 2?", "options": ["2", "3", "1", "0"], "answer": "3", "category": "Mathematics"},
    {"question": "How many sides does a hexagon have?", "options": ["5", "6", "7", "8"], "answer": "6", "category": "Mathematics"},
    {"question": "What is the cube root of 27?", "options": ["2", "3", "4", "9"], "answer": "3", "category": "Mathematics"},
    {"question": "What is 9 squared?", "options": ["18", "27", "81", "72"], "answer": "81", "category": "Mathematics"},
    {"question": "What is the median of 1, 3, 5, 7, 9?", "options": ["3", "5", "7", "4"], "answer": "5", "category": "Mathematics"},
    {"question": "What is the mode of 2, 2, 3, 4, 5?", "options": ["2", "3", "4", "5"], "answer": "2", "category": "Mathematics"},
    {"question": "What is the range of 10, 20, 30, 40?", "options": ["10", "20", "30", "40"], "answer": "30", "category": "Mathematics"},
    {"question": "What is 100 divided by 4?", "options": ["15", "20", "25", "30"], "answer": "25", "category": "Mathematics"},
    {"question": "What is the value of cos(0)?", "options": ["0", "1", "-1", "0.5"], "answer": "1", "category": "Mathematics"},
    {"question": "What is the value of sin(90 degrees)?", "options": ["0", "0.5", "1", "-1"], "answer": "1", "category": "Mathematics"},
    {"question": "What type of number is pi?", "options": ["Rational", "Irrational", "Integer", "Natural"], "answer": "Irrational", "category": "Mathematics"},
    {"question": "What is the volume of a cube with side 3?", "options": ["9", "18", "27", "36"], "answer": "27", "category": "Mathematics"},
    {"question": "What is the probability of rolling a 6 on a fair die?", "options": ["1/2", "1/3", "1/6", "1/12"], "answer": "1/6", "category": "Mathematics"},
    {"question": "What is the greatest common divisor of 12 and 18?", "options": ["2", "3", "6", "9"], "answer": "6", "category": "Mathematics"},
    {"question": "What is the least common multiple of 4 and 6?", "options": ["12", "24", "8", "2"], "answer": "12", "category": "Mathematics"},
    {"question": "What is 0.5 as a fraction?", "options": ["1/5", "1/4", "1/3", "1/2"], "answer": "1/2", "category": "Mathematics"},
    {"question": "What is the quadratic formula used for?", "options": ["Linear equations", "Quadratic equations", "Cubic equations", "Differential equations"], "answer": "Quadratic equations", "category": "Mathematics"},

    # Literature
    {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"], "answer": "William Shakespeare", "category": "Literature"},
    {"question": "Who wrote '1984'?", "options": ["Aldous Huxley", "George Orwell", "Ray Bradbury", "H.G. Wells"], "answer": "George Orwell", "category": "Literature"},
    {"question": "Who wrote 'To Kill a Mockingbird'?", "options": ["Harper Lee", "John Steinbeck", "Ernest Hemingway", "F. Scott Fitzgerald"], "answer": "Harper Lee", "category": "Literature"},
    {"question": "What is the first book of the Harry Potter series?", "options": ["Chamber of Secrets", "Philosopher's Stone", "Prisoner of Azkaban", "Goblet of Fire"], "answer": "Philosopher's Stone", "category": "Literature"},
    {"question": "Who wrote 'The Great Gatsby'?", "options": ["F. Scott Fitzgerald", "Ernest Hemingway", "John Steinbeck", "William Faulkner"], "answer": "F. Scott Fitzgerald", "category": "Literature"},
    {"question": "Who wrote 'Pride and Prejudice'?", "options": ["Charlotte Bronte", "Emily Bronte", "Jane Austen", "Charles Dickens"], "answer": "Jane Austen", "category": "Literature"},
    {"question": "Who wrote 'The Odyssey'?", "options": ["Sophocles", "Homer", "Virgil", "Plato"], "answer": "Homer", "category": "Literature"},
    {"question": "What is the name of the whale in Moby-Dick?", "options": ["Moby Dick", "White Whale", "Leviathan", "Great Whale"], "answer": "Moby Dick", "category": "Literature"},
    {"question": "Who wrote 'Crime and Punishment'?", "options": ["Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov", "Ivan Turgenev"], "answer": "Fyodor Dostoevsky", "category": "Literature"},
    {"question": "Who wrote 'The Catcher in the Rye'?", "options": ["J.D. Salinger", "Harper Lee", "Kurt Vonnegut", "John Updike"], "answer": "J.D. Salinger", "category": "Literature"},
    {"question": "Who wrote 'Don Quixote'?", "options": ["Gabriel Garcia Marquez", "Miguel de Cervantes", "Jorge Luis Borges", "Pablo Neruda"], "answer": "Miguel de Cervantes", "category": "Literature"},
    {"question": "Who wrote 'The Divine Comedy'?", "options": ["Boccaccio", "Petrarch", "Dante Alighieri", "Machiavelli"], "answer": "Dante Alighieri", "category": "Literature"},
    {"question": "What is the fictional land in 'The Lord of the Rings'?", "options": ["Narnia", "Westeros", "Middle-earth", "Earthsea"], "answer": "Middle-earth", "category": "Literature"},
    {"question": "Who wrote 'War and Peace'?", "options": ["Fyodor Dostoevsky", "Leo Tolstoy", "Anton Chekhov", "Nikolai Gogol"], "answer": "Leo Tolstoy", "category": "Literature"},
    {"question": "Who wrote 'The Adventures of Huckleberry Finn'?", "options": ["Mark Twain", "Ernest Hemingway", "William Faulkner", "Jack London"], "answer": "Mark Twain", "category": "Literature"},
    {"question": "Who wrote 'Frankenstein'?", "options": ["Bram Stoker", "Mary Shelley", "Edgar Allan Poe", "H.G. Wells"], "answer": "Mary Shelley", "category": "Literature"},
    {"question": "Who wrote 'The Picture of Dorian Gray'?", "options": ["Oscar Wilde", "George Bernard Shaw", "James Joyce", "W.B. Yeats"], "answer": "Oscar Wilde", "category": "Literature"},
    {"question": "Who wrote 'One Hundred Years of Solitude'?", "options": ["Gabriel Garcia Marquez", "Isabel Allende", "Jorge Luis Borges", "Mario Vargas Llosa"], "answer": "Gabriel Garcia Marquez", "category": "Literature"},
    {"question": "Who wrote 'The Hobbit'?", "options": ["J.R.R. Tolkien", "C.S. Lewis", "J.K. Rowling", "George R.R. Martin"], "answer": "J.R.R. Tolkien", "category": "Literature"},
    {"question": "Who wrote 'Brave New World'?", "options": ["George Orwell", "Aldous Huxley", "Ray Bradbury", "H.G. Wells"], "answer": "Aldous Huxley", "category": "Literature"},

    # Geography
    {"question": "What is the longest river in the world?", "options": ["Amazon", "Nile", "Mississippi", "Yangtze"], "answer": "Nile", "category": "Geography"},
    {"question": "What is the largest continent by area?", "options": ["Africa", "North America", "Asia", "Europe"], "answer": "Asia", "category": "Geography"},
    {"question": "What is the capital of France?", "options": ["London", "Berlin", "Madrid", "Paris"], "answer": "Paris", "category": "Geography"},
    {"question": "What is the smallest country in the world?", "options": ["Monaco", "Vatican City", "San Marino", "Liechtenstein"], "answer": "Vatican City", "category": "Geography"},
    {"question": "What desert is the largest hot desert?", "options": ["Gobi", "Kalahari", "Sahara", "Arabian"], "answer": "Sahara", "category": "Geography"},
    {"question": "What mountain is the tallest in the world?", "options": ["K2", "Mount Everest", "Kangchenjunga", "Lhotse"], "answer": "Mount Everest", "category": "Geography"},
    {"question": "What is the largest ocean?", "options": ["Atlantic", "Indian", "Pacific", "Arctic"], "answer": "Pacific", "category": "Geography"},
    {"question": "What country has the most people?", "options": ["India", "China", "United States", "Indonesia"], "answer": "India", "category": "Geography"},
    {"question": "What is the capital of Japan?", "options": ["Seoul", "Beijing", "Tokyo", "Bangkok"], "answer": "Tokyo", "category": "Geography"},
    {"question": "What is the longest mountain range on land?", "options": ["Himalayas", "Andes", "Rockies", "Alps"], "answer": "Andes", "category": "Geography"},
    {"question": "What is the largest lake by surface area?", "options": ["Lake Superior", "Caspian Sea", "Lake Victoria", "Lake Baikal"], "answer": "Caspian Sea", "category": "Geography"},
    {"question": "What is the deepest point in the ocean?", "options": ["Mariana Trench", "Tonga Trench", "Puerto Rico Trench", "Java Trench"], "answer": "Mariana Trench", "category": "Geography"},
    {"question": "What country is both in Europe and Asia?", "options": ["Greece", "Turkey", "Egypt", "Iran"], "answer": "Turkey", "category": "Geography"},
    {"question": "What river flows through London?", "options": ["Seine", "Thames", "Danube", "Rhine"], "answer": "Thames", "category": "Geography"},
    {"question": "What is the capital of Australia?", "options": ["Sydney", "Melbourne", "Canberra", "Perth"], "answer": "Canberra", "category": "Geography"},
    {"question": "What is the largest island in the world?", "options": ["Greenland", "New Guinea", "Borneo", "Madagascar"], "answer": "Greenland", "category": "Geography"},
    {"question": "What strait separates Asia from North America?", "options": ["Bosphorus", "Bering", "Gibraltar", "Malacca"], "answer": "Bering", "category": "Geography"},
    {"question": "What is the driest inhabited continent?", "options": ["Africa", "Australia", "Antarctica", "Asia"], "answer": "Australia", "category": "Geography"},
    {"question": "What country has the most time zones?", "options": ["Russia", "United States", "France", "China"], "answer": "France", "category": "Geography"},
    {"question": "What canal connects the Mediterranean to the Red Sea?", "options": ["Panama Canal", "Suez Canal", "Erie Canal", "Kiel Canal"], "answer": "Suez Canal", "category": "Geography"},

    # Technology
    {"question": "Who is considered the father of the computer?", "options": ["Alan Turing", "Charles Babbage", "John von Neumann", "Ada Lovelace"], "answer": "Charles Babbage", "category": "Technology"},
    {"question": "What does CPU stand for?", "options": ["Central Process Unit", "Central Processing Unit", "Computer Personal Unit", "Core Processing Unit"], "answer": "Central Processing Unit", "category": "Technology"},
    {"question": "What is the main language of the web?", "options": ["Python", "HTML", "C++", "Java"], "answer": "HTML", "category": "Technology"},
    {"question": "What does 'HTTP' stand for?", "options": ["HyperText Transfer Protocol", "High Transfer Text Protocol", "HyperText Transmission Protocol", "High-Tech Transfer Protocol"], "answer": "HyperText Transfer Protocol", "category": "Technology"},
    {"question": "What company developed the iPhone?", "options": ["Google", "Microsoft", "Apple", "Samsung"], "answer": "Apple", "category": "Technology"},
    {"question": "What is the binary representation of 5?", "options": ["100", "101", "110", "111"], "answer": "101", "category": "Technology"},
    {"question": "What does RAM stand for?", "options": ["Read Access Memory", "Random Access Memory", "Run Application Module", "Real-time Access Memory"], "answer": "Random Access Memory", "category": "Technology"},
    {"question": "Who created Linux?", "options": ["Richard Stallman", "Linus Torvalds", "Bill Gates", "Ken Thompson"], "answer": "Linus Torvalds", "category": "Technology"},
    {"question": "What does SQL stand for?", "options": ["Structured Query Language", "Simple Query Language", "Standard Query Language", "Sequential Query Language"], "answer": "Structured Query Language", "category": "Technology"},
    {"question": "What is the smallest unit of digital data?", "options": ["Byte", "Bit", "Nibble", "Word"], "answer": "Bit", "category": "Technology"},
    {"question": "What year was the first iPhone released?", "options": ["2005", "2006", "2007", "2008"], "answer": "2007", "category": "Technology"},
    {"question": "What does 'AI' stand for?", "options": ["Artificial Integration", "Artificial Intelligence", "Automated Intelligence", "Advanced Intelligence"], "answer": "Artificial Intelligence", "category": "Technology"},
    {"question": "What is the most popular programming language in 2024?", "options": ["Java", "C++", "Python", "JavaScript"], "answer": "Python", "category": "Technology"},
    {"question": "What company created the Android OS?", "options": ["Apple", "Google", "Microsoft", "Samsung"], "answer": "Google", "category": "Technology"},
    {"question": "What protocol is used for secure web communication?", "options": ["HTTP", "HTTPS", "FTP", "SMTP"], "answer": "HTTPS", "category": "Technology"},
    {"question": "What does 'DNS' stand for?", "options": ["Domain Name System", "Digital Network Service", "Data Network Security", "Domain Network Standard"], "answer": "Domain Name System", "category": "Technology"},
    {"question": "Who is known as the father of AI?", "options": ["Alan Turing", "John McCarthy", "Geoffrey Hinton", "Yann LeCun"], "answer": "Alan Turing", "category": "Technology"},
    {"question": "What is the decimal value of hex FF?", "options": ["128", "255", "256", "512"], "answer": "255", "category": "Technology"},
    {"question": "What programming paradigm does Python primarily support?", "options": ["Functional", "Object-oriented", "Procedural", "Declarative"], "answer": "Object-oriented", "category": "Technology"},
    {"question": "What does 'API' stand for?", "options": ["Application Programming Interface", "Application Process Integration", "Automated Program Interface", "Advanced Programming Interface"], "answer": "Application Programming Interface", "category": "Technology"},

    # Philosophy
    {"question": "Who said 'I think, therefore I am'?", "options": ["Plato", "Descartes", "Aristotle", "Kant"], "answer": "Descartes", "category": "Philosophy"},
    {"question": "Who wrote 'The Republic'?", "options": ["Aristotle", "Plato", "Socrates", "Cicero"], "answer": "Plato", "category": "Philosophy"},
    {"question": "Who is considered the father of Western philosophy?", "options": ["Plato", "Aristotle", "Socrates", "Thales"], "answer": "Socrates", "category": "Philosophy"},
    {"question": "What philosophical concept is Kant famous for?", "options": ["The categorical imperative", "The social contract", "The will to power", "The unexamined life"], "answer": "The categorical imperative", "category": "Philosophy"},
    {"question": "Who wrote 'Beyond Good and Evil'?", "options": ["Karl Marx", "Friedrich Nietzsche", "Arthur Schopenhauer", "Jean-Paul Sartre"], "answer": "Friedrich Nietzsche", "category": "Philosophy"},
    {"question": "What is the philosophical study of being called?", "options": ["Epistemology", "Ontology", "Ethics", "Aesthetics"], "answer": "Ontology", "category": "Philosophy"},
    {"question": "Who proposed the social contract theory?", "options": ["John Locke", "Thomas Hobbes", "Jean-Jacques Rousseau", "All of the above"], "answer": "All of the above", "category": "Philosophy"},
    {"question": "What is the study of knowledge called?", "options": ["Ontology", "Epistemology", "Metaphysics", "Logic"], "answer": "Epistemology", "category": "Philosophy"},
    {"question": "Who wrote 'Thus Spoke Zarathustra'?", "options": ["Immanuel Kant", "Friedrich Nietzsche", "Soren Kierkegaard", "Georg Hegel"], "answer": "Friedrich Nietzsche", "category": "Philosophy"},
    {"question": "What school of thought emphasizes individual existence and freedom?", "options": ["Stoicism", "Empiricism", "Existentialism", "Pragmatism"], "answer": "Existentialism", "category": "Philosophy"},

    # Astronomy
    {"question": "What is the name of Earth's only natural satellite?", "options": ["Titan", "Europa", "Moon", "Phobos"], "answer": "Moon", "category": "Astronomy"},
    {"question": "What type of star is the Sun?", "options": ["Red giant", "Yellow dwarf", "White dwarf", "Blue giant"], "answer": "Yellow dwarf", "category": "Astronomy"},
    {"question": "What is a group of stars called?", "options": ["Galaxy", "Constellation", "Cluster", "Nebula"], "answer": "Constellation", "category": "Astronomy"},
    {"question": "What is the largest moon of Jupiter?", "options": ["Io", "Europa", "Ganymede", "Callisto"], "answer": "Ganymede", "category": "Astronomy"},
    {"question": "What is a comet's tail made of?", "options": ["Rock", "Gas and dust", "Ice", "Plasma"], "answer": "Gas and dust", "category": "Astronomy"},
    {"question": "What astronomical event occurs when the Moon passes between Earth and Sun?", "options": ["Lunar eclipse", "Solar eclipse", "New moon", "Full moon"], "answer": "Solar eclipse", "category": "Astronomy"},
    {"question": "What is the nearest star to Earth after the Sun?", "options": ["Alpha Centauri", "Proxima Centauri", "Sirius", "Betelgeuse"], "answer": "Proxima Centauri", "category": "Astronomy"},
    {"question": "What is a dying star that has collapsed called?", "options": ["Red giant", "White dwarf", "Neutron star", "Black hole"], "answer": "White dwarf", "category": "Astronomy"},
    {"question": "What is the main belt of asteroids between?", "options": ["Mars and Jupiter", "Earth and Mars", "Jupiter and Saturn", "Venus and Earth"], "answer": "Mars and Jupiter", "category": "Astronomy"},
    {"question": "What year was Pluto reclassified as a dwarf planet?", "options": ["2004", "2005", "2006", "2007"], "answer": "2006", "category": "Astronomy"},

    # Biology
    {"question": "What controls the cell's activities?", "options": ["Nucleus", "Cytoplasm", "Cell membrane", "Mitochondria"], "answer": "Nucleus", "category": "Biology"},
    {"question": "What is the basic unit of life?", "options": ["Atom", "Molecule", "Cell", "Tissue"], "answer": "Cell", "category": "Biology"},
    {"question": "What system breaks down food?", "options": ["Respiratory", "Digestive", "Circulatory", "Nervous"], "answer": "Digestive", "category": "Biology"},
    {"question": "What organ pumps blood?", "options": ["Lungs", "Heart", "Liver", "Brain"], "answer": "Heart", "category": "Biology"},
    {"question": "What is the largest group in classification?", "options": ["Species", "Genus", "Kingdom", "Phylum"], "answer": "Kingdom", "category": "Biology"},
    {"question": "What is the molecule that carries genetic information?", "options": ["RNA", "DNA", "Protein", "Lipid"], "answer": "DNA", "category": "Biology"},
    {"question": "What process releases energy from glucose?", "options": ["Photosynthesis", "Respiration", "Digestion", "Fermentation"], "answer": "Respiration", "category": "Biology"},
    {"question": "What type of cell has a nucleus?", "options": ["Prokaryotic", "Eukaryotic", "Bacterial", "Archaeal"], "answer": "Eukaryotic", "category": "Biology"},
    {"question": "What is the study of living things called?", "options": ["Biology", "Chemistry", "Physics", "Geology"], "answer": "Biology", "category": "Biology"},
    {"question": "What system fights infection?", "options": ["Nervous", "Immune", "Endocrine", "Circulatory"], "answer": "Immune", "category": "Biology"},

    # Chemistry
    {"question": "What is the lightest element?", "options": ["Helium", "Hydrogen", "Lithium", "Beryllium"], "answer": "Hydrogen", "category": "Chemistry"},
    {"question": "What is the chemical symbol for silver?", "options": ["Si", "Sv", "Ag", "Au"], "answer": "Ag", "category": "Chemistry"},
    {"question": "What is the chemical symbol for lead?", "options": ["Ld", "Pb", "Le", "Pl"], "answer": "Pb", "category": "Chemistry"},
    {"question": "What is the pH of lemon juice?", "options": ["2", "5", "7", "9"], "answer": "2", "category": "Chemistry"},
    {"question": "What type of reaction absorbs heat?", "options": ["Exothermic", "Endothermic", "Catalytic", "Redox"], "answer": "Endothermic", "category": "Chemistry"},
    {"question": "What is the most abundant element in Earth's crust?", "options": ["Aluminum", "Silicon", "Oxygen", "Iron"], "answer": "Oxygen", "category": "Chemistry"},
    {"question": "What is the chemical formula for ammonia?", "options": ["NH3", "NO2", "N2O", "NH4"], "answer": "NH3", "category": "Chemistry"},
    {"question": "What is the process of a solid turning directly into gas?", "options": ["Melting", "Boiling", "Sublimation", "Condensation"], "answer": "Sublimation", "category": "Chemistry"},
    {"question": "What element has the symbol 'C'?", "options": ["Calcium", "Carbon", "Cobalt", "Copper"], "answer": "Carbon", "category": "Chemistry"},
    {"question": "What is the common name for dihydrogen monoxide?", "options": ["Hydrogen peroxide", "Water", "Hydrochloric acid", "Methane"], "answer": "Water", "category": "Chemistry"},

    # Physics
    {"question": "What is Newton's first law about?", "options": ["Gravity", "Inertia", "Action-reaction", "Acceleration"], "answer": "Inertia", "category": "Physics"},
    {"question": "What law states energy cannot be created or destroyed?", "options": ["First law of thermodynamics", "Second law of thermodynamics", "Newton's third law", "Ohm's law"], "answer": "First law of thermodynamics", "category": "Physics"},
    {"question": "What is the unit of power?", "options": ["Joule", "Watt", "Newton", "Volt"], "answer": "Watt", "category": "Physics"},
    {"question": "What type of wave is light?", "options": ["Mechanical", "Transverse", "Longitudinal", "Surface"], "answer": "Transverse", "category": "Physics"},
    {"question": "What is the acceleration due to gravity on Earth (m/s^2)?", "options": ["8.9", "9.8", "10.8", "7.8"], "answer": "9.8", "category": "Physics"},
    {"question": "What law relates voltage, current, and resistance?", "options": ["Coulomb's law", "Ohm's law", "Faraday's law", "Ampere's law"], "answer": "Ohm's law", "category": "Physics"},
    {"question": "What is the speed of light approximately (km/s)?", "options": ["300,000", "150,000", "500,000", "100,000"], "answer": "300,000", "category": "Physics"},
    {"question": "What particle mediates the electromagnetic force?", "options": ["Gluon", "Photon", "Boson", "Graviton"], "answer": "Photon", "category": "Physics"},
    {"question": "What is the change in velocity over time called?", "options": ["Speed", "Velocity", "Acceleration", "Momentum"], "answer": "Acceleration", "category": "Physics"},
    {"question": "What law states for every action there is an equal reaction?", "options": ["Newton's first", "Newton's second", "Newton's third", "Newton's fourth"], "answer": "Newton's third", "category": "Physics"},
]


class CalibrationDataset:
    def __init__(self, num_questions: int = 300, seed: int = 42):
        self.num_questions = num_questions
        self.seed = seed
        self.questions = self._build_dataset()

    def _build_dataset(self) -> List[Dict]:
        rng = random.Random(self.seed)
        num_full_cycles = self.num_questions // len(QUESTIONS_DATA)
        remainder = self.num_questions % len(QUESTIONS_DATA)

        pool = QUESTIONS_DATA * num_full_cycles
        pool += rng.sample(QUESTIONS_DATA, remainder)

        for q in pool:
            rng.shuffle(q["options"])

        return pool

    def __len__(self) -> int:
        return len(self.questions)

    def __getitem__(self, idx: int) -> Dict:
        return self.questions[idx]

    def get_categories(self) -> List[str]:
        return list(set(q["category"] for q in self.questions))

    def get_by_category(self, category: str) -> List[Dict]:
        return [q for q in self.questions if q["category"] == category]

    def to_dicts(self) -> List[Dict]:
        return self.questions

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.questions, f, indent=2)

    @staticmethod
    def format_prompt(question: str, options: List[str]) -> str:
        lines = [f"Question: {question}", "", "Options:"]
        for i, opt in enumerate(options):
            lines.append(f"{chr(65 + i)}. {opt}")
        lines.append("")
        lines.append("Answer with only the letter of the correct option (A, B, C, or D).")
        lines.append("Then state your confidence as a percentage (0-100%).")
        return "\n".join(lines)
