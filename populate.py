from os import environ
environ.setdefault('DJANGO_SETTINGS_MODULE','exam_board.settings')

import django
django.setup()

import random
from general.models import AcademicYear, User, Student, Course, Assessment, AssessmentResult, AcademicYear, LevelHead
from django.db import connection, reset_queries
import time
import traceback

# random.seed(0)
##SETUP
FIRST_YEAR_OF_COURSES = 2018
LAST_YEAR_OF_COURSES = 2022
CURRENT_YEAR = 2022
COMPUTER_SCIENCE_COURSE_CODE_PREFIX = 'COMPSCI'
REQUIRED_CREDITS_PER_COURSE = 120

TOTAL_NUMBER_OF_USERS = 20
TOTAL_NUMBER_OF_COURSES = 5*12 #5 years of courses, 12 courses for lvl 1,2,3,4,5
LEVEL_PATTERN = [1,2,3,4,5]
TOTAL_NUMBER_OF_STUDENTS = 600

def decision(probability):
    return random.random() < probability

class Populator:
    def __init__(self):
        self.users = []
        self.students = []
        self.courses = []
        self.assessment_groups = []  # will store groups of assessments that weigh up to 100%
        self.assessment_results = []

        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear.objects.create(year=CURRENT_YEAR, is_current=True)
        self.current_academic_year = academic_year.year

        #extra randomization settings
        #the 2 settings below are used to bias the start year of students, so that more students start closer towards the first year of courses.
        self.range_of_start_years = range(FIRST_YEAR_OF_COURSES, self.current_academic_year + 1)
        self.start_years_weights = [1/i for i in self.range_of_start_years]
    
    #https://catonmat.net/tools/generate-random-names - names generated from here
    first_names = """Mark,Menachem,Clinton,Suzanne,Juliann,Brook,Treyton,Brandi,Leroy,Manuel,Cristofer,Nathanael,Isaiah,Dahlia,Noa,Jaila,Hazel,Ireland,Jeniffer,Annabella,Brenton,Caroline,Dangelo,Chassidy,Jacklyn,Howard,Cali,Zachariah,Mariel,Keanu,Lawson,Tony,Elexis,Sydni,Jajuan,Juliette,Averi,Bobby,Oswaldo,Nicholas,Jennifer,Moses,Brea,April,Sienna,Nakia,Sara,Neil,Kaylea,Kenya,Chynna,Mariana,Christopher,Jaleel,Ambria,Harmony,Beatrice,Kole,August,Rianna,Francesco,Kent,Eugene,Devin,Dan,Adonis,Katharine,Maverick,Aidan,Elijah,Dara,Makena,Johnson,Gabriel,Leonard,Kaden,Connor,Raheem,Preston,Alesha,Ammon,Precious,Danny,Shirley,Chester,Sean,Hailie,Ryland,Theresa,Alecia,Astrid,Joselyn,Christen,Andrew,Dayton,Edmund,Adriel,Jaycie,Erik,Denis,Brynn,Kristofer,Ramon,Colleen,Syed,Mariela,Chyna,Robyn,Irene,Ellie,Deontae,Jamar,Gissell,Leanna,Victoria,Marilyn,Dianna,Arthur,Marquis,Brandon,Braedon,Conner,Arielle,Ari,Anaya,Mia,Efren,Jay,Rey,Patrick,Sarah,Kendell,Luiz,Alia,Antwan,Killian,Camilla,Arjun,Alonso,Justus,Kinsley,Amiyah,Desean,Logan,Javier,Zayne,Anita,Eddy,Alayna,Riley,Cloe,Stefan,Robin,Jacquelin,Clara,Sasha,Steven,Jakobe,Tai,Jonas,Bridgett,Harold,Esteban,Lynsey,Zion,Aliza,Kennedy,Perry,Alek,Mustafa,Jaqueline,Karlee,Keaton,Benito,Savanah,Deondre,Kara,Caylee,Rosario,Kellie,Calvin,Frankie,Luis,Maggie,Courtney,Dante,Gwyneth,Lauryn,Maxine,Yusuf,Darnell,Deshaun,Raven,Jarod,Quinton,Alyson,Isabelle,Reagan,Bruce,Frida,Katherine,Jensen,Eve,Alexia,Eliana,Mateo,Keisha,Adelaide,Thaddeus,Princess,Austen,Keyla,Dominick,Reilly,Dale,Federico,Wayne,Brad,Bobbie,Chris,Lori,Sequoia,Jordy,Alvaro,Camron,Shawn,Lionel,Tayler,Siena,Quintin,Bowen,Joselin,Ean,Fabiola,Kaya,Gavin,Jaylyn,Donovan,Rivka,Brett,Edwin,Alissa,Kathrine,Andreas,Danae,Adeline,Stefany,Bernadette,Roxanne,Brock,Sebastien,Nathalia,Herbert,Amiah,Gerald,Daria,Kyler,Sheila,Tyree,Marion,Bryson,Harper,Jessie,Jude,Dorothy,Jonah,Vera,Kerry,Adrian,Aubrey,Lacy,Kendal,Gordon,Kiarra,Abriana,Jasmyne,Alliyah,Blayne,Yehuda,Deonte,Mekhi,Gustavo,Kelton,Tylor,Addison,Paloma,Sam,Latrell,Travis,Camila,Emely,Yamilet,Yosef,Chaim,Dora,Kaliyah,Zackary,Jill,Janae,Anabelle,Nathaly,Misael,Raelynn,Mikel,Kianna,Norma,Immanuel,Octavio,Keri,Reina,Trystan,Alyssia,Jordyn,Grace,Nicolas,Demarco,Marla,Deion,Benny,Jackelyn,Arman,Rylie,Teagan,Iyanna,Mindy,Markus,Malaysia,Zariah,Vincent,Asia,Wesley,Tyreek,Aman,Alivia,Keyana,June,Rhett,Aysia,Alexys,Natasha,Cheyanne,Renee,Esther,Destin,Lorena,Elaine,Joan,Jamari,Jaylin,Trevion,Mitchell,Ananda,Amir,Kalvin,Josie,Susan,Fernanda,Shivani,Corina,Ryan,Janice,Alaina,Alina,Amia,Myron,Lance,Meagan,Elyssa,Simon,Yahaira,Alanna,Kallie,Keelan,Salma,Carli,Tianna,Quinlan,Ashtyn,Eden,Macy,Bronson,Kiera,Lilia,Tanisha,Kyara,Kamryn,Baby,Clifton,Enoch,Nick,Yasmeen,Dalila,Chase,Kaylee,Terri,Tyriq,Hailee,Joseph,Kory,Jovany,Mckenzie,Kelis,Gianni,Jalyn,Constance,Amari,Emilio,Moises,Keith,Ahmad,Santiago,Aric,Floyd,Damon,Lamar,Caden,Lena,Vaughn,Lisa,Alejandra,Mckinley,Makala,Abdul,Garett,Kori,Annette,Skye,Deon,Karleigh,Jarvis,Aylin,Vladimir,Jerimiah,Allen,Aaron,Bailey,Anastasia,Elias,Amirah,Aria,Maleah,Chelsey,Emmanuel,Keandre,Tessa,Leann,Madeline,Parker,Daniel,Blake,Jermaine,Yajaira,Pilar,Ashlin,Wyatt,Annalisa,Joaquin,Angeles,Anderson,China,Alonzo,Milan,Dillon,Jean,Christa,Lucinda,Donte,Enzo,Jamal,Muhammad,Glenn,Tate,Chad,Allan,Long,Valery,Elisha,Anastacia,Kierra,Graham,Jarrod,Ashlee,Kristian,Justyn,Johnathan,Franco,Hector,Brisa,Destiny,Ayla,Trae,Helen,Jarred,Jaret,Sydnee,Yulissa,Jerry,Dallas,Liana,Daquan""".split(",")
    last_names = """Gannon,Augustine,Cordero,Bohannon,Gandy,Loya,Samuels,Teal,Ali,Turley,Stinson,Lindberg,Wu,Givens,Truong,Davila,Messina,Merchant,Harkins,Nunley,Staley,Giles,Close,Farrell,Ayres,Galvan,Gibson,Kim,Allen,Strange,Headley,Moulton,Kaufman,Lovell,Randall,Beyer,Storm,Santiago,Sisson,Delossantos,Lamb,Cary,Kerns,Marcus,Shuler,Pace,Ware,George,Gilman,Shipley,Cranford,Magee,Hale,Ritter,Huber,Hawes,Coker,Davey,Greenwood,Provost,Lassiter,Heckman,Dye,Bower,Barbee,Burnette,Livingston,Lira,Davis,Rudd,Priest,Honeycutt,Waterman,Prado,Peyton,Olson,Frost,Myers,Rourke,Riggins,Sands,Bradshaw,Demers,Ferrara,Putnam,Bell,Bock,Nesbitt,Fenton,Avalos,Wilburn,Huggins,Lay,Rosales,Houston,Burt,Villarreal,Farnsworth,Tompkins,Wade,Bohn,Larue,Colbert,Murdock,Outlaw,Zapata,Meyer,Rojas,McCorkle,Bruce,Partridge,Mears,Rahman,Graves,Meadows,Atwood,Calkins,Dawson,Kyle,Stewart,Daly,Espinosa,Eng,Rosen,Betz,Custer,Nevarez,Dodson,Jack,Ojeda,Madrigal,Monroe,Scruggs,Vasquez,Rainey,Emery,Millan,Rosario,Briscoe,Gale,Kirkland,Emmons,Gorman,Carrera,Dooley,Ivey,Santamaria,High,Zhao,Amaral,Rich,Thurston,Hare,Simpson,Ritchey,Segura,Gaskins,Becker,Sales,Franklin,Holliday,Larson,Cooley,McCord,Wall,Robinson,Cady,Crider,Cardwell,Barnett,Grogan,Noe,Aldridge,Dick,Branch,Lindquist,Chase,Jerome,David,Bowen,Atkins,Woodruff,Duvall,Morrow,Arthur,Richard,Coyne,Moran,Mcvey,Bond,Jaeger,Wynne,Blalock,Miles,Valdivia,Marquis,Maki,Adamson,Gifford,Freeland,Hager,Buckley,Aguayo,Conover,Call,Lombardi,Newton,Minter,Michaels,Carrasco,Meyers,Dotson,Bridges,Comstock,Knox,Driscoll,Russell,Spears,Harden,Kopp,Newkirk,Belcher,Graff,Painter,Graber,Burke,Bigelow,Hawks,Grayson,Archuleta,Day,Smalls,Solis,Hagen,Evans,Mayfield,Currier,Herrmann,Delgadillo,Desimone,Stepp,Zambrano,Garay,Justice,Green,Culbertson,Champion,Kee,Perales,Lemke,Laney,Faircloth,Garibay,Kasper,Carden,Burdette,Marquardt,Napier,Abrams,Connell,Stock,Stacy,Chin,Martins,Hostetler,Westmoreland,Alfaro,Lawler,Garrett,Gray,Nagel,Bourne,Acker,Boyle,Tobin,Craft,Brill,Jaime,Goforth,Meador,Fultz,Coulter,Gallo,Hammons,Manuel,Tierney,Barnette,Hawthorne,Watters,Bowman,Carrington,Moore,Gupta,Zink,Boudreau,Hill,Kirsch,Mays,Spalding,Breeden,Herrington,Weems,Blue,Mason,Burrows,Erickson,Brandenburg,Villasenor,Boss,Lawless,Crouch,Medlin,Ogden,Barlow,Kenney,Easley,Adame,Clouse,Murray,Rafferty,Leung,Conn,Keegan,Marr,Pelletier,Eastman,Braswell,Crane,Stamper,Casper,Sage,Blanco,Meehan,Pina,Linares,Florez,Gomez,Stone,Bergman,Milner,Church,Sigler,Stratton,Barnhart,Dahl,Copeland,Mireles,Schofield,Bergeron,Barrett,Borges,Land,Lively,Winston,Solorzano,Jameson,Galindo,Pearce,Norman,Brothers,Caruso,Vines,Palermo,Derrick,Gauthier,Akin,German,Gilbert,Lovett,Sherrill,Ackerman,Jorgensen,Rau,Foley,Benedict,Carbone,Ruth,Fuchs,Heller,Dodds,Burton,Hitchcock,Rodrigues,Schmidt,Forsyth,Schubert,Wheeler,Whiteside,Ruff,Tejada,Wilbur,Pritchett,Conti,Wing,Jacoby,Mount,Winstead,Sorenson,Dion,Kirby,Marcum,Infante,Skinner,Hester,Huey,Satterfield,Cornell,Grey,Humphreys,Baughman,Himes,Rico,Carr,Coe,Velez,Eckert,Kilgore,Alvarado,Ruiz,Kendrick,Marvin,Larkin,Dial,Gregory,Herron,Hussain,Locke,Steffen,Broyles,Berry,Clevenger,Hood,Connolly,Whitfield,Seibert,Arredondo,Scully,Ferguson,Bennett,Casas,Fabian,Zimmerman,Hoskins,Toler,Herzog,Royal,Blackmon,Hairston,Thomason,Humphrey,Ellsworth,Sewell,Rhoades,Laster,Lindley,Ostrander,Parham,Langdon,Reynoso,Her,Holland,Britt,Estep,Quintero,Davison,Lovelace,Schroeder,Dodge,Giron,Sauer,Starkey,Lewis,Gatlin,Fisher,Galvez,Marx,Crews,Polanco,Brennan,Guerra,Peralta,Peace,Harder,See,Rhoads,Richards,Hatton,Goodrich,Alonzo,Shanahan,Aparicio,Dover,Lemus,Luttrell,Hinkle,Dix,Alarcon,Lusk,Kidwell,Owens,Jiang,Burgess,Jacques,Holley,Shelton,Reaves,Horowitz,Byler,Irvine,New,Branson,Ortiz,Haugen,Stephenson,Dube,Talbot,Shepard,Witte,Stiles,Tully,Cochran,Kirk,Rush,Argueta,Mcnabb,Bivens,Straub,Steiner,Power,Sheets,Ayala,Counts,Rees,Amos,Wofford,Scherer,Behrens,Trujillo,Travis,Caron,Albers,Mattson,Elkins,Acevedo,Daigle,Zhang,Mora,Oh,Kaiser,Madrid,Desantis,Burks,Spence,Walsh,Ryder,Ricci,Koehler,Bruns,Somers,Drew,Burnham,Epstein,Crocker,Borden,McClendon,Ashford,Chavis,Gilbertson,Hite,Bowens,Polk,Weatherford,Hassan,Bland,Epperson,Judd,Herring,Puente,Christman,Landis,Quinlan,Tan,Baer,Culp,Estes,Lynn,Peter,Paredes,Titus,Agnew,Mosier,Nagy,Doll,Catalano,Neil,Mahon,Clifton,Carlton,Reynolds,Piper,Jeffries,Hooks,Kenyon,Clinton,Godwin,Morris,Vetter,Fontaine,Shannon,Hallman,Hurst,Vargas,Cave,Bandy,Marino,Rosenthal,Forte,Brewer,Cox,Reddick,Glenn,Irvin,Hayden,Pickering,Denton,Turk,Parson,Heath,Venegas,Carman,Castle,Mejia,Whalen,Walden,Vaughan,Strand,Castellano,McCollum,Branham,Van,Laws,Sizemore,Burkhart,Dang,Danner,Varela,Swisher,Keener,Norris,Matheny,Koch,Carlson,Duong,Swartz,Hardwick,Royer,Duckworth,Motley,Corrales,Chacon,Mahan,Charles,Littleton,Ulrich,Kinney,Diaz,Rock,Weiner,Guidry,Chan,Coles,Rector,Burroughs,Best,Irving,Lanning,Merrill,Lenz,Heard,Quigley,Ireland,Grove,Kunz,Sanford,Malcolm,Santos,Mack,Hofer,Espinoza,Abbott,Willingham,Kane,Samples,Forman,Post,Parkinson,Stoner,Kohler,Corey,Stubbs,Dukes,Cheng,Dennis,Nettles,Shore,Quick,Brinkman,Houser,Oswald,Mathew,Prieto,Squires,Masterson,Lantz,McDonough,Solano,Orr,Neal,Pollack,Haley,Allison,Cody,Phelan,Curtin,Latimer,Jarrell,Toledo,Mcalister,Joe,Avila,Ross,Dutton,Beaulieu,Kohl,Montano,McDaniel,Huston,Armendariz,Brunson,Ball,Park,Mackenzie,Zavala,Toth,Calvert,Woods,Vandyke,Cole,Carney,Collins,Dozier,Toro,Solomon,Banuelos,Quinn,Muniz,Reis,Lanham,Jonas,Layne,Yoder,Swain,Harrell,McIntyre,Reinhardt,Butcher,Fontenot,Haase,Shoemaker,Mundy,Hargrove,Cummins,Crisp,Guy,Sexton,Roush,Dewey,McNally,Oliva,Devries,Hartmann,Baumgartner,Bright,Bruno,Blaylock,Runyon,Shanks,Sinclair,Isom,Byrnes,Leger,Duval,Hahn,Sosa,Whitworth,Gilley,Hopson,Zarate,Busby,Chaffin,Kay,Beatty,Manzo,Geary,Leblanc,Elam,Walker,Vickery,Clay,Davenport,Fugate,Bernal,Kohn,Wertz,Collazo,Neff,Kaur,Marlow,Stafford,Nye,Gaston,Hills,Halstead,Bernstein,Andrews,Carey,Packer,Batista,Thompson,Conway,Barksdale,Mateo,Thai,Ragan,Leary,Mohamed,Case,Louis,Wheatley,Herman,Pond,Starr,Chow,Perrin,Montanez,Reich,Hoffman,Robins,Ferry,Kemper,Fletcher,Andrus,Kaminski,Plunkett,Elias,Barfield,Jackson,Coon,Brumfield,Delvalle,Canfield,McGraw,Staggs,Nickerson,Shea,Wellman,Higgs,Unger,Kimmel,Oldham,Cartwright,Hayes,Burrell,Saylor,Griffith,Coppola,Isbell,Dowdy,Ervin,Crawford,Steed,Mello,Uribe,Earle,Meredith,Compton,Cordell,Fritz,McKinnon,Champagne,Horst,Swann,Bullock,Saxton,Brubaker,Colby,Brock,Woo,Greenfield,McGowan,Bronson,Findley,McLeod,Pepper,Miranda,Negron,Bush,Christopher,Casteel,Swanson,Thiel,Dehart,Waggoner,Riggs,Crenshaw,Earley,Mattox,Skaggs,Bellamy,Farris,Noyes,Escamilla,Zepeda,Peterson,Andres,Robertson,Mosley,Hiller,Andersen,Bradley,Jimenez,Clarke,Snyder,Tran,Naylor,Wingate,Hanley,Strong,Pringle,Goebel,Simon,Schreiber,Arnett,Biddle,Small,Brown,Grubbs,Dallas,Fox,McMullen,Hancock,Lin,Mize,Keenan,Henley,Windham,Rosenberg,North,Reno,Wadsworth,Puckett,Calloway,Faust,Gagne,Trevino,Roman,Willey,Mercer,Trapp,Trimble,Freed,Beckett,Elliot,Cramer,Needham,Bertrand,Brinson,Moffitt,Valle,Middleton,Liles,Flint,Yeager,Sherman,Kincaid,Lemay,Higgins,Allard,Harlan,Blount,Stine,Deal,Ayers,Bratton,Berrios,Hubert,Enriquez,Morrell,Krebs,Hand""".split(",")
    degree_titles = ["BSc", "BEng", "Msc", "MEng"]

    @property
    def random_full_name(self):
        return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
    
    @property
    def random_user_data(self):
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"
        return {
            "username": username,
            "password": "password",
            "email": f"{username}@example.com",
            "first_name": first_name,
            "last_name": last_name,
            "title": random.choices(["Dr", "Prof"], weights=[0.65, 0.35])[0],
        }
    
    @property
    def random_student_data(self):
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        guid = f"{random.randint(1000000, 9000000)}{last_name[0]}"

        degree_title = random.choices(self.degree_titles, weights=[0.40, 0.25, 0.25, 0.10])[0]
        if "Eng" in degree_title:
            degree_name = "Software Engineering"
        else:
            degree_name = "Computing Science"

        is_masters = degree_title in ["Msc", "MEng"]
        is_faster_route = decision(0.1)
        ##earliest possible year should have at least some students who are in their final year (even masters.)
        ##add courses for all their levels ? eks dee
        start_year_padding = random.choices([0, 1, 2, 3], weights=[0.65, 0.20, 0.10, 0.05])[0]
        start_academic_year = random.choices(self.range_of_start_years, weights=self.start_years_weights)[0] - start_year_padding

        end_academic_year = start_academic_year + 3
        if degree_title.startswith("M"):
            end_academic_year += 1
        if is_faster_route:
            end_academic_year -= 1
        
        #if already graduated - current level is the level they graduated at. Otherwise, it's the level they're currently on
        if self.current_academic_year >= end_academic_year: #if already graduated
            current_level = end_academic_year - start_academic_year + (2 if is_faster_route else 1)
        else: #eg. start 2020, end 2023, current 2022 -> level = 3 if normal, 4 if faster route
            current_level = (self.current_academic_year - start_academic_year) + (2 if is_faster_route else 1)
        
        return {
            "full_name": f"{first_name} {last_name}",
            "GUID": guid,
            "degree_name": degree_name,
            "degree_title": degree_title,
            "is_faster_route": is_faster_route,
            "is_masters": is_masters,
            "start_academic_year": start_academic_year,
            "end_academic_year": end_academic_year,
            "current_level": current_level
        }
    
    def random_course_data(self, level):
        academic_year = random.randint(FIRST_YEAR_OF_COURSES, LAST_YEAR_OF_COURSES)
        course_level = level
        course_code = f"{COMPUTER_SCIENCE_COURSE_CODE_PREFIX}{course_level}{random.randint(100, 999)}"
        name = f"Computing Science {course_code[-4:]}"
        lecturer_comment = f"Welcome to {name}!"
        credits = random.choices([10, 20], weights=[0.80, 0.20])[0]

        if course_level == 5:
            name += "(M)"
        
        is_taught_now = (academic_year == self.current_academic_year)
        
        return {
            "code": course_code,
            "name": name,
            "academic_year": academic_year,
            "lecturer_comment": lecturer_comment,
            "credits": credits,
            "is_taught_now": is_taught_now,
        }
    
    def generate_users(self, n):
        self.users = [User(**self.random_user_data) for _ in range(n)]
        print(f"Generated {len(self.users)} users")
    
    def generate_assessment_groups(self):
        self.assessment_groups.append([   
            Assessment(name="Assignment 1", type="C", weighting=10),
            Assessment(name="Assignment 2", type="C", weighting=20),
            Assessment(name="Question 1", type="E", weighting=35),
            Assessment(name="Question 2", type="E", weighting=35)
        ])
        self.assessment_groups.append([   
            Assessment(name="Moodle quizzes", type="C", weighting=5),
            Assessment(name="Assignment 1", type="C", weighting=15),
            Assessment(name="Question 1", type="E", weighting=25),
            Assessment(name="Question 2", type="E", weighting=25),
            Assessment(name="Question 3", type="E", weighting=30)
        ])
        self.assessment_groups.append([   
            Assessment(name="Assignment 1", type="C", weighting=10),
            Assessment(name="Project", type="G", weighting=35),
            Assessment(name="Presentation", type="G", weighting=5),
            Assessment(name="Question 1", type="E", weighting=25),
            Assessment(name="Question 2", type="E", weighting=25)
        ])
        self.assessment_groups.append([  
            Assessment(name="Web application (frontend)", type="G", weighting=25),
            Assessment(name="Web application (backend)", type="G", weighting=30),
            Assessment(name="Presentation", type="G", weighting=5),
            Assessment(name="Question 1", type="E", weighting=10),
            Assessment(name="Question 2", type="E", weighting=15),
            Assessment(name="Question 3", type="E", weighting=15),
        ])
        self.assessment_groups.append([   
            Assessment(name="Quizzes", type="C", weighting=10),
            Assessment(name="Research poster", type="C", weighting=40),
            Assessment(name="Exam question 1", type="E", weighting=25),
            Assessment(name="Exam question 2", type="E", weighting=25),
        ])
        self.assessment_groups.append([ #Individual project
            Assessment(name="Dissertation", type="I", weighting=85),
            Assessment(name="Profesional conduct", type="I", weighting=10),
            Assessment(name="Presentation", type="I", weighting=5),
        ])
        self.assessment_groups.append([ #Group project
            Assessment(name="Dissertation", type="G", weighting=70),
            Assessment(name="Profesional conduct", type="G", weighting=20),
            Assessment(name="Presentation", type="G", weighting=10),
        ])
        # exam grade = grade of all Assessments with type E, including their weightings

    def generate_students(self, n):
        self.students.extend([Student(**self.random_student_data) for _ in range(n)])
        print(f"Generated {n} students")
    
    def generate_courses(self, n):
        i = 0
        courses = []
        ##hardcode generate lvl 3 group and level 4 individual project courses for all the years
        lecturers = random.choices(self.users, k=3)
        random_numbers = random.sample(range(100, 999), 3)
        for j in range(FIRST_YEAR_OF_COURSES, LAST_YEAR_OF_COURSES+1):
            courses.append(Course(academic_year=j, code=f"{COMPUTER_SCIENCE_COURSE_CODE_PREFIX}3{random_numbers[0]}", name="Level 3 Group project", credits=40, lecturer_comment="Welcome to the level 3 group project!", is_taught_now=(j == self.current_academic_year), lecturer=lecturers[0]))
            courses.append(Course(academic_year=j, code=f"{COMPUTER_SCIENCE_COURSE_CODE_PREFIX}4{random_numbers[1]}", name="Level 4 Individual project", credits=40, lecturer_comment="Welcome to the level 4 individual project!", is_taught_now=(j == self.current_academic_year), lecturer=lecturers[1]))
            courses.append(Course(academic_year=j, code=f"{COMPUTER_SCIENCE_COURSE_CODE_PREFIX}5{random_numbers[2]}", name="Level 5 (M) Individual project", credits=60, lecturer_comment="Welcome to the level 5 (M) individual project!", is_taught_now=(j == self.current_academic_year), lecturer=lecturers[2]))

        while i < n:
            i+=1
            level = LEVEL_PATTERN[i%len(LEVEL_PATTERN) - 1]
            course_data = self.random_course_data(level)
            if decision(0.95):
                course_data["lecturer"] = random.choice(self.users)
            else:
                course_data["lecturer_comment"] = "No lecturer assigned to the course yet!"

            courses.append(Course(**course_data))
            for j in range(FIRST_YEAR_OF_COURSES, LAST_YEAR_OF_COURSES + 1):  # add the same course across other years as well (80% chance)
                if not course_data["academic_year"] == j:
                    course_data_copy = course_data.copy()
                    course_data_copy["academic_year"] = j
                    course_data_copy["is_taught_now"] = course_data_copy["academic_year"] == self.current_academic_year
                    courses.append(Course(**course_data_copy))
        
        self.courses=courses
        print(f"Generated {i} courses")

    def create_admin(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@gmail.com", "1234")
    
    def generate_assessment_results(self):
        def get_assessment_list(course):
            if "Individual" in course.name:
                assessment_list = self.assessment_groups[-2]
            elif "Group" in course.name:
                assessment_list = self.assessment_groups[-1]
            else:
                assessment_list = random.choice(self.assessment_groups[:-2])
            return assessment_list
        
        start = time.process_time()
        reset_queries()
        courses = Course.objects.all().prefetch_related("students").order_by("code")
        prev_course_code = courses[0].code
        assessment_list = get_assessment_list(courses[0])

        grade_range = [i for i in range(23)]
        good_grade_dist = [i**2.6 for i in range(23)]
        avg_grade_dist = [1 for _ in range (5)] + [2 for _ in range (5)] + [10 for _ in range (9)] + [3 for _ in range (4)]
        bad_grade_dist = [i**1.2 for i in range(7)] + [i for i in range(10, -1, -1)] + [0.5 for _ in range(5)]
        peformance_choices = [bad_grade_dist, avg_grade_dist, good_grade_dist]

        student_performance_map = {student.id: random.choices(peformance_choices, weights=[0.20, 0.525, 0.275], k=1)[0] for student in self.students}
        for course in courses:
            if course.code != prev_course_code: #new course found!
                prev_course_code = course.code
                assessment_list = get_assessment_list(course)
            
            course_students = course.students.all()
            
            course.assessments.set(assessment_list)  # course_assessment_m2m table has been populated
            for student in course_students:
                all_mv = decision(0.025) #2.5% chance of all assessments being marked as MV (the course grade is voided medical)
                for assessment in assessment_list:
                    self.assessment_results.append(AssessmentResult(
                        student=student,
                        course=course,
                        assessment=assessment,
                        grade=random.choices(grade_range, weights=student_performance_map.get(student.id, avg_grade_dist), k=1)[0], #grade is weighted towards higher grades
                        preponderance=random.choices(['NA', 'MV', 'CW', 'CR'], weights=[0.85, 0.1, 0.025, 0.025])[0] if not all_mv else 'MV', ## 85% chance of NA, 10% chance of MV, 2.5% chance of CW, 2.5% chance of CR, OR all MV if all_mv is True
                    )
                )
        
        print(f"Generated {len(self.assessment_results)} assessment results in {time.process_time() - start} seconds and {len(connection.queries)} queries")

    def fetch_courses_total_credits(self, candidate_courses, total_credits):
        if not candidate_courses:
            return []

        course_set = []
        credits_total = 0
        attempt_course = random.choice(candidate_courses)
        attempts = 0
        while attempts < 10:
            if credits_total + attempt_course.credits <= total_credits:
                course_set.append(attempt_course)
                credits_total += attempt_course.credits
                candidate_courses.remove(attempt_course)
                attempts = 0
            else:
                attempts += 1

            if credits_total == total_credits or len(candidate_courses) == 0:
                return course_set
            attempt_course = random.choice(candidate_courses)
        return course_set
    
    #course -> enrolled students.
    #iterate over all students, 

    def populate_database(self):
        print("Transferring current state into database")
        try:
            User.objects.bulk_create(self.users, ignore_conflicts=True)
            print(f"Transferred {len(self.users)} users succesfully")
            level_heads = []
            for i in range(FIRST_YEAR_OF_COURSES, LAST_YEAR_OF_COURSES + 1):
                year = AcademicYear.objects.create(year=i, is_current=i==self.current_academic_year)
                for j, user in enumerate(random.choices(self.users, k=5), start=1):##5 random users are level heads for each year
                    level_heads.append(LevelHead(user=user, academic_year=year, level=j))
            LevelHead.objects.bulk_create(level_heads, ignore_conflicts=True)
            print("Populated level heads and academic years")

            students = Student.objects.bulk_create(self.students, ignore_conflicts=True)
            print(f"Transferred {len(students)} students succesfully")
            courses = Course.objects.bulk_create(self.courses, ignore_conflicts=True)

            print(f"Transferred {len(courses)} courses succesfully")
            
            reset_queries()
            start = time.process_time()
            candidate_courses = list(Course.objects.filter(credits__lte=20, credits__gte=10).all())
            for student in students:
                if decision(0.01):  # 99% of students will be enrolled into courses.
                    continue
                final_courses_for_all_years = []

                #2020, current lvl 3, at 2020 means lvl 3
                for level, year in enumerate(range(student.start_academic_year, student.start_academic_year + student.current_level + 1), start=1): ##add 120 credits worth of courses, or less, for each year of study.
                    if student.is_faster_route:
                        level += 1
                    if level > student.current_level:
                        break

                    must_have_course = None
                    if level == 1:
                        allowed_levels = [1]
                    elif level == 2:
                        allowed_levels = [2] if not student.is_faster_route else [1,2]
                    elif level == 3:
                        must_have_course = Course.objects.filter(academic_year=year, name__contains="Group", credits=40).first()
                        allowed_levels = [3, 4]
                    elif level == 4:
                        allowed_levels = [3, 4, 5]
                        must_have_course = Course.objects.filter(academic_year=year, name__contains="Individual", credits=40).first()
                    elif level == 5:
                        allowed_levels = [5]
                        must_have_course = Course.objects.filter(academic_year=year, name__contains="Individual", credits=60).first()

                    required_credits = REQUIRED_CREDITS_PER_COURSE - must_have_course.credits if must_have_course else REQUIRED_CREDITS_PER_COURSE
                    if decision(0.08): ##small chance to enroll 10 or 20 extra credits worth of courses!
                        required_credits += random.choices([10,20], weights=[0.9,0.1], k=1)[0]
                    elif decision(0.05): ##small chance to enroll 10-30 less credits worth of courses
                        required_credits -= random.choices([10,20,30], weights=[0.50, 0.40, 0.10], k=1)[0]
                    course_setup = [must_have_course] if must_have_course else []
                    candidate_courses_for_year = [course for course in candidate_courses if course.academic_year == year and course.level_integer in allowed_levels]
                    course_setup.extend(self.fetch_courses_total_credits(candidate_courses_for_year, required_credits))

                    final_courses_for_all_years.extend(course_setup)
                
                student.courses.add(*final_courses_for_all_years)
            print(f"Ran {len(connection.queries)} queries and took {time.process_time() - start} seconds to enroll {len(self.students)} students to {len(self.courses)} courses")

            #remove courses that have no students enrolled in them.
            courses_no_students = Course.objects.filter(students=None)
            print(f"Number of courses deleted, with no students enrolled in them: {courses_no_students.count()}")
            courses_no_students.delete()
            
            assessments = Assessment.objects.bulk_create([assessment for assessment_group in self.assessment_groups for assessment in assessment_group], ignore_conflicts=True)
            print(f"Transferred {len(assessments)} assessments succesfully")

            self.generate_assessment_results() ##generate assessment results for all students, necessary here since it requires students to already be in the database
            assessment_results = AssessmentResult.objects.bulk_create(self.assessment_results, ignore_conflicts=True)
            print(f"Transferred {len(assessment_results)} assessment results succesfully")
        except Exception as e:
            print("Failed to populate database", e)
            traceback.print_exc()
            return
    
    def wipe_database(self):
        print("Wiping database...")
        try:
            User.objects.all().delete()
            AcademicYear.objects.all().delete()
            Student.objects.all().delete()
            Course.objects.all().delete()
            Assessment.objects.all().delete()
            AssessmentResult.objects.all().delete()
            
            print("Wiped database succesfully")
        except Exception as e:
            print("Failed to wipe database", e)
            return

def main():
    print("Generating population data...")
    populator = Populator()
    populator.wipe_database()
    populator.create_admin()
    populator.generate_users(TOTAL_NUMBER_OF_USERS)
    populator.generate_students(TOTAL_NUMBER_OF_STUDENTS)
    populator.generate_courses(TOTAL_NUMBER_OF_COURSES)
    populator.generate_assessment_groups()

    populator.populate_database()

if __name__ == "__main__":
    main()