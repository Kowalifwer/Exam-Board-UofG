from os import environ
environ.setdefault('DJANGO_SETTINGS_MODULE','exam_board.settings')

import django
django.setup()

import random
from general.models import AcademicYear, User, Student, Course, Assessment, AssessmentResult, AcademicYear
from django.utils import lorem_ipsum
from django.db import connection, reset_queries

def decision(probability):
    return random.random() < probability

class Populator:
    def __init__(self):
        self.students = []

        self.courses = []

        self.assessments = []
        self.assessment_results = []

        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear.objects.create(year=2022, is_current=True)
        self.current_academic_year = academic_year.year
    
    #https://catonmat.net/tools/generate-random-names - names generated from here
    first_names = """Mark,Menachem,Clinton,Suzanne,Juliann,Brook,Treyton,Brandi,Leroy,Manuel,Cristofer,Nathanael,Isaiah,Dahlia,Noa,Jaila,Hazel,Ireland,Jeniffer,Annabella,Brenton,Caroline,Dangelo,Chassidy,Jacklyn,Howard,Cali,Zachariah,Mariel,Keanu,Lawson,Tony,Elexis,Sydni,Jajuan,Juliette,Averi,Bobby,Oswaldo,Nicholas,Jennifer,Moses,Brea,April,Sienna,Nakia,Sara,Neil,Kaylea,Kenya,Chynna,Mariana,Christopher,Jaleel,Ambria,Harmony,Beatrice,Kole,August,Rianna,Francesco,Kent,Eugene,Devin,Dan,Adonis,Katharine,Maverick,Aidan,Elijah,Dara,Makena,Johnson,Gabriel,Leonard,Kaden,Connor,Raheem,Preston,Alesha,Ammon,Precious,Danny,Shirley,Chester,Sean,Hailie,Ryland,Theresa,Alecia,Astrid,Joselyn,Christen,Andrew,Dayton,Edmund,Adriel,Jaycie,Erik,Denis,Brynn,Kristofer,Ramon,Colleen,Syed,Mariela,Chyna,Robyn,Irene,Ellie,Deontae,Jamar,Gissell,Leanna,Victoria,Marilyn,Dianna,Arthur,Marquis,Brandon,Braedon,Conner,Arielle,Ari,Anaya,Mia,Efren,Jay,Rey,Patrick,Sarah,Kendell,Luiz,Alia,Antwan,Killian,Camilla,Arjun,Alonso,Justus,Kinsley,Amiyah,Desean,Logan,Javier,Zayne,Anita,Eddy,Alayna,Riley,Cloe,Stefan,Robin,Jacquelin,Clara,Sasha,Steven,Jakobe,Tai,Jonas,Bridgett,Harold,Esteban,Lynsey,Zion,Aliza,Kennedy,Perry,Alek,Mustafa,Jaqueline,Karlee,Keaton,Benito,Savanah,Deondre,Kara,Caylee,Rosario,Kellie,Calvin,Frankie,Luis,Maggie,Courtney,Dante,Gwyneth,Lauryn,Maxine,Yusuf,Darnell,Deshaun,Raven,Jarod,Quinton,Alyson,Isabelle,Reagan,Bruce,Frida,Katherine,Jensen,Eve,Alexia,Eliana,Mateo,Keisha,Adelaide,Thaddeus,Princess,Austen,Keyla,Dominick,Reilly,Dale,Federico,Wayne,Brad,Bobbie,Chris,Lori,Sequoia,Jordy,Alvaro,Camron,Shawn,Lionel,Tayler,Siena,Quintin,Bowen,Joselin,Ean,Fabiola,Kaya,Gavin,Jaylyn,Donovan,Rivka,Brett,Edwin,Alissa,Kathrine,Andreas,Danae,Adeline,Stefany,Bernadette,Roxanne,Brock,Sebastien,Nathalia,Herbert,Amiah,Gerald,Daria,Kyler,Sheila,Tyree,Marion,Bryson,Harper,Jessie,Jude,Dorothy,Jonah,Vera,Kerry,Adrian,Aubrey,Lacy,Kendal,Gordon,Kiarra,Abriana,Jasmyne,Alliyah,Blayne,Yehuda,Deonte,Mekhi,Gustavo,Kelton,Tylor,Addison,Paloma,Sam,Latrell,Travis,Camila,Emely,Yamilet,Yosef,Chaim,Dora,Kaliyah,Zackary,Jill,Janae,Anabelle,Nathaly,Misael,Raelynn,Mikel,Kianna,Norma,Immanuel,Octavio,Keri,Reina,Trystan,Alyssia,Jordyn,Grace,Nicolas,Demarco,Marla,Deion,Benny,Jackelyn,Arman,Rylie,Teagan,Iyanna,Mindy,Markus,Malaysia,Zariah,Vincent,Asia,Wesley,Tyreek,Aman,Alivia,Keyana,June,Rhett,Aysia,Alexys,Natasha,Cheyanne,Renee,Esther,Destin,Lorena,Elaine,Joan,Jamari,Jaylin,Trevion,Mitchell,Ananda,Amir,Kalvin,Josie,Susan,Fernanda,Shivani,Corina,Ryan,Janice,Alaina,Alina,Amia,Myron,Lance,Meagan,Elyssa,Simon,Yahaira,Alanna,Kallie,Keelan,Salma,Carli,Tianna,Quinlan,Ashtyn,Eden,Macy,Bronson,Kiera,Lilia,Tanisha,Kyara,Kamryn,Baby,Clifton,Enoch,Nick,Yasmeen,Dalila,Chase,Kaylee,Terri,Tyriq,Hailee,Joseph,Kory,Jovany,Mckenzie,Kelis,Gianni,Jalyn,Constance,Amari,Emilio,Moises,Keith,Ahmad,Santiago,Aric,Floyd,Damon,Lamar,Caden,Lena,Vaughn,Lisa,Alejandra,Mckinley,Makala,Abdul,Garett,Kori,Annette,Skye,Deon,Karleigh,Jarvis,Aylin,Vladimir,Jerimiah,Allen,Aaron,Bailey,Anastasia,Elias,Amirah,Aria,Maleah,Chelsey,Emmanuel,Keandre,Tessa,Leann,Madeline,Parker,Daniel,Blake,Jermaine,Yajaira,Pilar,Ashlin,Wyatt,Annalisa,Joaquin,Angeles,Anderson,China,Alonzo,Milan,Dillon,Jean,Christa,Lucinda,Donte,Enzo,Jamal,Muhammad,Glenn,Tate,Chad,Allan,Long,Valery,Elisha,Anastacia,Kierra,Graham,Jarrod,Ashlee,Kristian,Justyn,Johnathan,Franco,Hector,Brisa,Destiny,Ayla,Trae,Helen,Jarred,Jaret,Sydnee,Yulissa,Jerry,Dallas,Liana,Daquan""".split(",")
    last_names = """Knutson,Greenwood,Pyle,Hodges,Venable,Pappas,Newman,Gilliland,Cordell,Carlos,Booth,Gallardo,Barclay,Durham,Hairston,Cone,Prince,Cannon,Alvarez,Matson,Skaggs,Kasper,Barajas,Xiong,Coyle,Siegel,Rodgers,Way,Duke,Sousa,Kilgore,Trinidad,Katz,Diaz,Yoon,Arnett,Feldman,Fontaine,Turley,Lumpkin,Chao,Crane,Hinojosa,Gilbert,Coley,Bunch,Courtney,Thao,Thurman,Gallegos,Turner,Persaud,Waters,Ross,Velasco,Cohn,Trout,Zhu,Razo,Moss,Carbajal,Linton,Hood,Handley,Schoen,Julian,Applegate,Pemberton,Lynch,Beal,Whitworth,Florez,Hoffman,Montez,Meredith,Desantis,Nicholas,Hogan,Clapp,Lawler,VanHorn,Bridges,Stahl,Field,House,Toth,Cleveland,Zambrano,Whittaker,Boyer,Loveless,Clarkson,Bayer,Barnhart,Millard,Jeffries,Duncan,Cherry,Wilcox,Medley,Wynn,Rudd,Stoll,Brumfield,Ma,Sherrill,Ferguson,Lam,Biddle,Berg,Creech,Black,Heller,Parish,Hay,Arroyo,Easley,Mcghee,Tubbs,Weston,Rosas,Britton,Rosales,Drury,Hanks,Angulo,Alfonso,Piazza,Jefferson,Shanahan,Doucette,Bagwell,Romo,Lanning,Wozniak,Archer,Jacoby,Larkin,Amaya,McLaughlin,Hutto,Pritchard,Ragsdale,Tsai,Jernigan,Perrin,Donahue,Rice,Evans,Griffin,McMahan,Everhart,Winston,Alcala,Ceballos,Brinkman,Kahn,Reynolds,Roche,Knudsen,Neal,Daigle,Robledo,Meyer,McRae,Shaw,Tarver,Bentley,Finney,Serna,Dunlap,Still,Jensen,Ruggiero,Lyman,Colwell,Foust,Wenzel,Greco,Hough,Oshea,Himes,Dudley,Odell,Custer,Fanning,Crowley,Wilde,Prescott,Alaniz,Sowell,Bryant,Huddleston,Stoddard,Dang,Heaton,Little,Kelso,Peace,Hunt,Deal,Eldridge,Morris,Diggs,Swift,Horowitz,Frias,Venegas,Giordano,Medina,Hagen,Crum,Streeter,Francis,Hutton,Walter,McCarter,Morales,London,Bills,Gamboa,Mann,Weber,Lacey,Gauthier,Pickett,Miller,Rendon,Sorensen,McDuffie,McGregor,Isaac,Brill,Dahl,Gibbons,Jauregui,Aquino,Jarrett,Keating,Straub,Turpin,Ralston,Marsh,Hershberger,Hurt,Ransom,Connor,Agnew,Fuller,Evers,Schaefer,Stuckey,Stout,Delong,Ling,Breaux,Stringer,Inman,Hastings,Dangelo,Berger,Hassan,Royer,Knowles,Le,Cavanaugh,Bowles,Holt,Castellanos,Hollins,Gould,Quinlan,Torres,Schuler,Shuman,Arndt,Kenyon,Sprague,Cameron,Ko,Mullis,Schuster,Thomason,Beauchamp,Henning,Barth,Munoz,Hollingsworth,Ellison,Overstreet,Luna,Baggett,Salcedo,Newcomb,Yi,Fortner,Dennison,Neff,Gregg,Bullock,Dye,Solomon,Lindsey,Sterling,Estrella,Cheatham,Welker,Thiel,Olivarez,Mize,Muhammad,Guenther,Washington,Broome,Dodson,Crowe,Rojas,Carvalho,Casteel,Stubblefield,Dillard,Skidmore,Adame,Kelsey,Hodge,Andersen,Ruffin,Gagne,Whipple,Argueta,Baum,Sisson,Kennedy,Webster,Connors,Kirchner,Mcnabb,Cahill,Becerra,Stanton,Harvey,Shore,Canada,Luu,Boyd,Burdette,McCann,Simpkins,McConnell,Dunaway,Caudill,Schofield,Crockett,Bailey,Ocampo,Franco,Olsen,Baxter,Calvin,Merchant,Rawls,Bruno,Fortune,Howe,Sutter,Gilmore,Ferry,Stubbs,Suarez,Simms,Viera,Chung,Rizzo,Armendariz,Banuelos,Becker,Frey,Lorenz,Morin,Windham,Redman,Velasquez,Menendez,Myles,Ott,Malley,Ogden,Sandberg,Fulton,Fleming,Bronson,Franz,Mackey,Luttrell,Ellsworth,Rivera,Hardin,Calloway,Akins,Chandler,Montalvo,Armenta,MacDonald,Olivares,Keen,Dent,Rodriquez,Daly,Eddy,Brannon,Willingham,Desimone,Valenzuela,Gore,Hill,Shea,Milligan,Lau,Mayes,Earl,Allison,Ordonez,Wofford,Cardwell,Vigil,Landers,Graber,Prieto,Garvey,Loy,Padgett,Regan,Vang,Hedges,Iverson,Bender,Beaty,Tyson,Stepp,Melvin,Grantham,Gray,Sheppard,Coffman,Valadez,Bonner,Catalano,Quintero,Pauley,McCracken,Dinh,Keaton,Wiles,Oliveira,Myers,Delacruz,Butts,Hensley,Pack,Weems,Ceja,Browning,Stpierre,Tobias,Seeley,Slade,Fleck,Reno,Byrd,Jameson,Read,Clouse,Aleman,Pettit,Krieger,Tyree,Birch,Forster,Rouse,Johns,Sells,Chisholm,Church,Ho,Koenig,Valdez,Charles,Gonzalez,Sullivan,Granger,Whiteside,Steen,Hurst,Gresham,Hogue,Page,New,Dunham,Lindley,Quinn""".split(",")
    degree_titles = ["BSc", "BEng", "Msc", "MEng", "PhD"]

    @property
    def random_full_name(self):
        return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
    
    @property
    def random_student_data(self):
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        guid = f"{random.randint(1000000, 9000000)}{last_name[0]}"

        degree_title = random.choices(self.degree_titles, weights=[0.45, 0.3, 0.1, 0.1, 0.05])[0]
        is_faster_route = decision(0.1)
        is_masters = degree_title in ["Msc", "MEng"]
        start_academic_year = random.randint(2018, 2022)
        end_academic_year = start_academic_year + 4 if degree_title.startswith("B") else start_academic_year + 5
        current_academic_year = random.randint(start_academic_year, self.current_academic_year)
        
        return {
            "full_name": f"{first_name} {last_name}",
            "GUID": guid,
            "degree_title": degree_title,
            "is_faster_route": is_faster_route,
            "is_masters": is_masters,
            "start_academic_year": start_academic_year,
            "end_academic_year": end_academic_year,
            "current_academic_year": current_academic_year,
        }
    
    @property
    def random_course_data(self):
        academic_year = random.randint(2018, 2023)
        course_code = f"COMPSCI{random.randint(1,5)}{random.randint(100, 999)}"

        name = f"Computing Science {course_code[-4:]}"
        lecturer_comments = "".join(lorem_ipsum.paragraphs(random.randint(0,2), False))

        credits = random.choices([10, 20, 40, 60], weights=[0.70, 0.20, 0.075, 0.025])[0]
        if credits == 40:
            name = f"{random.choice(['Individual', 'Group'])} PROJECT - {course_code}"
        elif credits == 60:
            name = f"{random.choice(['Individual', 'Group'])} PROJECT (MSC) - {course_code}"
        is_taught_now = academic_year == self.current_academic_year
        
        return {
            "code": course_code,
            "name": name,
            "academic_year": academic_year,
            "lecturer_comments": lecturer_comments,
            "credits": credits,
            "is_taught_now": is_taught_now,
        }
    
    
    def generate_assessments(self):
        self.assessments.append(Assessment(name="Assignment 1", type="A", weighting=10))
        self.assessments.append(Assessment(name="Assignment 2", type="A", weighting=20))
        self.assessments.append(Assessment(name="Exam question 1", type="E", weighting=35))
        self.assessments.append(Assessment(name="Exam question 2", type="E", weighting=35))
        # exam grade = grade of all Assessments with type E, including their weightings

    def generate_students(self, n):
        self.students.extend([Student(**self.random_student_data) for _ in range(n)])
        print(f"Generated {n} students")
    
    def generate_courses(self, n):
        i = 0
        courses = []
        while i < n:
            course_data = self.random_course_data
            courses.append(Course(**course_data))
            i += 1
            for j in range(2018, 2023):
                if not course_data["academic_year"] == j and i < n and decision(0.75):
                    course_data_copy = course_data.copy()
                    course_data_copy["academic_year"] = j
                    course_data_copy["is_taught_now"] = course_data_copy["academic_year"] == self.current_academic_year
                    courses.append(Course(**course_data_copy))
                    i += 1
        
        self.courses=courses
        print(f"Generated {n} courses")

    def create_admin(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@gmail.com", "1234")
    
    def generate_assessment_results(self):
        for student in Student.objects.all().prefetch_related("courses"):
            courses = student.courses.all()
            for course in courses:
                for assessment in self.assessments:
                    self.assessment_results.append(AssessmentResult(
                        student=student,
                        course=course,
                        assessment=assessment,
                        grade=random.randint(0, 100),
                        preponderance=random.choices(['NA', 'MV', 'CV', 'CR'], weights=[0.75, 0.15, 0.05, 0.05])[0],
                    ))
        

    def populate_database(self):
        print("Transferring current state into database")
        try:
            students = Student.objects.bulk_create(self.students, ignore_conflicts=True)
            print(f"Transferred {len(students)} students succesfully")
            courses = Course.objects.bulk_create(self.courses, ignore_conflicts=True)
            print(f"Transferred {len(courses)} courses succesfully")
            for course in courses:
                course.enrolled_students.set(random.sample(students, int(random.randint(0, len(students)*0.1))))
            print("Enrolled students into courses succesfully")

            assessments = Assessment.objects.bulk_create(self.assessments, ignore_conflicts=True)
            print(f"Transferred {len(assessments)} assessments succesfully")

            self.generate_assessment_results()
            assessment_results = AssessmentResult.objects.bulk_create(self.assessment_results, ignore_conflicts=True)
            print(f"Transferred {len(assessment_results)} assessment results succesfully")
        except Exception as e:
            print("Failed to populate database", e)
            return
    
    def wipe_database(self):
        print("Wiping database")
        try:
            Student.objects.all().delete()

            print("Deleted all students")
            Course.objects.all().delete()
            print("Deleted all courses")
            Assessment.objects.all().delete()
            print("Deleted all assessments")
            AssessmentResult.objects.all().delete()
            print("Deleted all assessment results")
        except Exception as e:
            print("Failed to wipe database", e)
            return

def main():
    print("Generating population data...")
    populator = Populator()
    populator.create_admin()
    populator.wipe_database()
    populator.generate_students(2000)
    populator.generate_courses(75)
    populator.generate_assessments()
    populator.populate_database()


if __name__ == "__main__":
    main()