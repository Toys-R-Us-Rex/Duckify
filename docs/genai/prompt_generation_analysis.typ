#let pc(x,s,y) = [#figure(
  image("prompt_result/" + x, width: s),
  caption : y,
)]

= Prompt Analysis

This document will regroup a serie of prompt tests run during the equivalent of a half day. The objective of this serie of prompt was to test a new approach of prompt and also give more time for the former GenAI team to work on other element. The main add I did in the prompt was to add an initiale statement : "A rubber duck disguised as". Maybe it could help the process to signify that what we provide a duck as entry. 

 == Police officer

What we can intuit from our perception of what is a police officer : their uniform are mainly black or dark blue : at least in the dark tune. So it's not so surprising to see that the first example is mainly black. 

 #pc("1_policeman/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a police officer")

With the addition a specific palette (red, yellow, blue, white) we could expect the result would tend to have more "standard tone" but we can see that the "blue" part tends to be more dark blue than blue. The reason is surely that the common color is (as said before) likely to tend to black and dark blue and as you can see it's dark blue so the palette is respected.

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

 Addding any additionnal detail seems not to modify how the model think a police officer looks like. Maybe investigate with more constraint could be a solution but it also means that if adding more constraint is necessary and makes it works, we should investigate to have a global additionnal descriptive prompt to the base that a user could write (we can assume that a user doesn't want write a complete an descriptive prompt).

#pagebreak()
== Animals 

The second thematic was to see if we could recognize animal on a duck only by its texture (aka its skin). I will only show 2 animals but keep in mind that in some cases the texture (skin) only is not enough to recognize the animal. The one you will see next seems to work pretty well in general but we can anticipate that some result will be totally not accurate (can also be altered by the paletisation). The conclusion of this part is that animal that can only be described by its texture would be a good candidate as simple prompt.

=== Cow

 This is a non-exhaustive list of result but we can observe 2 type of result :

 - One with the beak in the original color (yellow)
 - The palette constraint apply also to the beak (as asked)

 This kind of constraint-overpassing is not really a problem in this situation (but technically it is). 

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

=== Cheetah

Another easy-describe animal from its texture (skin) 

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

=== Bee

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

== Video game character

We tested some classic superheroes (superman and batman) and the result were relatively accurate. So I wondered if the result could be the same for characters from video game. I choosed 2 that I consider well-known enough so I could expect that MV-Adapter could know them. In fact it's not the case as you can see in the following picture. The result could also come from the fact that these characters can't be match in another shape than the caracter should be. To verify that, I should have tried theses prompt with corresponding model (Mario and Link).

=== Mario

What we should see in the result :

A palette of brown, red, blue and eventually white (we consider that if we see yellow it's because there is no texture at this place)

For Mario, we have a beginning of a acceptable result : the palette is more or less correct with what we would expect but as said in the introduction of the Video game charcacter. Proably matching this duck model to a humanoid that is not necessary defined by only its costume isn't totally possible with a simple prompt. It conclude also in the sence that we should introduce a more precise prompt but is it feasible case by case ? Technically yes but realistically we should build a description case by case which is too much for the time remaining and also maybe not a main objective (other method should be added to improve quality).

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

=== Link

Strangly this try is a complete fail : the only "correct" point of theses 2 prompt is the presence of green in the first, as the character is mainly green. After theses two generation, I decided not to investigate more on that point

#pc("4_Link/Link.jpg", 20%, "Character model example")
#pc("4_Link/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as Link the main character of the video game serie The legend of Zelda")
#pc("4_Link/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as Link the main character of the video game serie The legend of Zelda")

#pagebreak()
== Zombie



#pc("5_zombie/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a zombie")
#pc("5_zombie/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a zombie")


== Jobs

This part was a continuity of prompt made by the former member of team GenAi on jobs : I tried 2 aspect :

- If a well-defined patern cloth can be apply to the duck (soldier)
- And if a tool from a specific job could appear on the duck (doctor)

=== Soldier with camouflage

For the first, without the common weird texture the result are pretty good. In my opinion the best result of this document.

#pc("7_soldier_camouflage/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a military soldier with camouflage clothes patern and a green face")
#pc("7_soldier_camouflage/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a military soldier with camouflage clothes patern and a green face")

=== Doctor 

For this part, as said in the introduction of this section, I tried to add a specific tool to the duck, here a stetoscope : I expected to have some line that go around the neck of the duck and maybe a circle linked to this line : In some result we can see this line but more no than yes. I also try to apply a precise texture to the wings but it seems that the recognition of the model's wings is not consistent.

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
== Historical theme

In this part, we can see what I also consider as good result base on what I expected. The main problem will be the detail for painting

=== Pharaon

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

=== Geisha


#pc("6_geisha/textured_official_model_1.png", 80%, "Prompt: A rubber duck disguised as a geisha")
#pc("6_geisha/textured_official_model_2.png", 80%, "Prompt: A rubber duck disguised as a geisha")


#pagebreak()

== Special texture from manga

Here I tried to generate a specific element from a specific domain. I tried to apply to the duck a patern similar that you can see just bellow : this is a pretty well-known element from a well-known manga called Naruto. We can conclude many things with this test :
- The recognition of the eye of the duck model is pretty fine but the application of the specific texture is a failure. Maybe the reason is similar to the video game, it's a well-known domain for me but not necessary for MV-Adapter.
- Also maybe the prompt was overcharged of detail : ninja, a specific manga (maybe not well-defined), specific patern on the eyes.

#pc("12_ninja_special_eye/sharingan.jpg", 10%, "Illustration of what the patern asked for the eye is(from Naruto manga)")
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

== Rubik's cube

The exercice here was to see if MV-Adapter is able to correctly structure the patern on the duck. Obviously the task is not easy and with the test I did I can't determine if the problem is to apply texture from a cube object to a duck-shaped object or if MV-Adapter manages with difficutly to form a correct patern. In the example the result are satisfying but not really corresponding 100% to what a user could expect.

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


= Conclusion

In this document we can see that the result of the different generations are more or less satisfied but the quality is not better that what we could see during the past presentation and result from the GenAI team. 
My impression of this test session is that the model doesn't have all the knowledge of all theme (which is understandable with the constraint of time and power we have). Irregularity still occure in the same frequency : trying to add external context such as *"duck disguised as"* is not enough for increasing significally the quality of generation. At least, that's what I notice, maybe my pannel of test is not exhaustive (it is not obviously but "only" 1 day was allocated for this task and event with more time, would it be worth to keep trying theses test). 

Some well-known domain (expected to be well-known) was not executed correctly (Video game and manga) probably because of the copyright around theses theme but in the other hand we manage to generate some BD character (batman and superman) that should also have some copyright around them. Any furhter investigation would be to generate this prompt on matching model (Mario on a mario model, ...).

However, as expected, job are pretty well represented : soldier and doctor were quite satisfying (still with weird result but that doesn't come from the prompt in my opinion). The same conclusion can be said for historical theme (geisha and pharaon) : the result are what we could expect. The problem would be more on the feasability of theses textures by the robot (base on pen restriction or robot precision).