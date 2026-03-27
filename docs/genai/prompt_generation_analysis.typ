#let pc(x,s,y) = [#figure(
  image("prompt_result/" + x, width: s),
  caption : y,
)]

= Prompt Analysis

This document will regroup a serie of prompt tests run during the equivalent of a half day. The objective of this serie of prompt was to test a new approach of prompt and also give more time for the former GenAI team to work on other element. The main add I did in the prompt was to add an initiale statement : "A rubber duck disguised as". Maybe it could help the process to signify that what we provide a duck as entry. 

 == Police officer

What we can intuit from our perception of what is a police officer. Their uniform are mainly black or dark blue : at least in the dark tune

 #pc("1_policeman/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a police officer")
 #pc("1_policeman/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white")
 #pc("1_policeman/textured_official_model_3.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white")
 #pc("1_policeman/textured_official_model_4.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_5.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_6.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_7.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_8.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_9.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_10.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_11.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_12.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")
 #pc("1_policeman/textured_official_model_13.png", 80%, "Prompt: A rubber duck disguised as a police officer with only red yellow blue white small sheriff star like western sheriff")

#pagebreak()
 == Cow 

 This is a non-exhaustive list of result 

 #pc("2_cow/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_5.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_9.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_13.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_16.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_19.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_21.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_24.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")
 #pc("2_cow/textured_official_model_27.png", 80%, "Prompt: A rubber duck disguised as a cow with white skin and black stain using only black and white")

== Video game character

We tested some classic superheroes (superman and batman) and the result were relatively accurate. So I wondered if the result could be the same for characters from video game. I choosed 2 that I consider well-known enough so I could expect that MV-Adapter could know them. In fact it's not the case as you can see in the following picture. 


#pagebreak()
=== Mario



#pc("3_Mario/Mario.jpg", 20%, " Character model example")
#pc("3_Mario/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_3.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_4.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_5.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_6.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_7.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_8.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_9.png", 80%, "Prompt: A rubber duck disguised as Mario")
#pc("3_Mario/textured_official_model_10.png", 80%, "Prompt: A rubber duck disguised as Mario")

#pagebreak()
=== Link



#pc("4_Link/Link.jpg", 20%, "Character model example")
#pc("4_Link/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as Link the main character of the video game serie Zelda")
#pc("4_Link/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as Link the main character of the video game serie Zelda")

#pagebreak()
== Zombie



#pc("5_zombie/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a zombie")
#pc("5_zombie/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a zombie")


#pagebreak()
== Geisha



#pc("6_geisha/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a geisha")
#pc("6_geisha/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a geisha")


#pagebreak()
== Soldier with camouflage



#pc("7_soldier_camouflage/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a military soldier with camouflage clothes patern and a green face")
#pc("7_soldier_camouflage/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a military soldier with camouflage clothes patern and a green face")

#pagebreak
== Doctor 

#pc("8_doctor/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_3.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_4.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_5.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_6.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_7.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_8.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_9.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_10.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")
#pc("8_doctor/textured_official_model_11.png", 80%, "Prompt: A rubber duck disguised as a doctor with white blouse, blue wings and a stethoscope around his neck and a blue cap on his head")

#pagebreak()
== Pharaon

#pc("9_pharaon/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_3.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_4.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_5.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_6.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_7.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_8.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_9.png", 80%, "Prompt: A rubber duck disguised as a pharaon")
#pc("9_pharaon/textured_official_model_10.png", 80%, "Prompt: A rubber duck disguised as a pharaon")


#pagebreak()
== Bee

#pc("11_bee/textured_duck_uv_v2_1.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_2.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_3.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_4.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_5.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_6.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_7.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_8.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_9.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")
#pc("11_bee/textured_duck_uv_v2_10.png", 80%, "Prompt: A rubber duck disguised as a bee with yellow and black patern")

#pagebreak()
== Special texture from manga

#pc("12_ninja_special_eye/example.jpg", 10%, "Illustration of what sharigan is (Source: https://pngtree.com/freepng/sharingan-eyes-of-uchiha-from-naruto-vector_15322284.html")
#pc("12_ninja_special_eye/textured_duck_uv_v2_1.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_2.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_3.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_4.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_5.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_6.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_7.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_8.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_9.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")
#pc("12_ninja_special_eye/textured_duck_uv_v2_10.png", 80%, "Prompt: A rubber duck disguised as a ninja of Naruto anime with sharigan on his eyes")

#pagebreak()
== Cheetah



#pc("13_cheetah/textured_duck_uv_v2_1.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_2.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_3.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_4.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_5.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_6.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_7.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_8.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_9.png", 80%, "Prompt: A rubber duck disguised as a cheetah")
#pc("13_cheetah/textured_duck_uv_v2_10.png", 80%, "Prompt: A rubber duck disguised as a cheetah")

#pagebreak()
== Rubik's cube



#pc("14_rubik_cube/textured_duck_uv_v2_1.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_2.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_3.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_4.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_5.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_6.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_7.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_8.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_9.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")
#pc("14_rubik_cube/textured_duck_uv_v2_10.png", 80%, "Prompt: A rubber duck with the texture of a rubik cube, with only white, yellow, red, blue, green, pink")