#Makefile for Controller

NAME = wheeltest

CC = gcc
LIB = -framework IOKit -framework CoreFoundation
INC = -I include
SRC = hid.c wheel.c

all: $(NAME)

$(NAME):
	@$(CC) $(LIB) $(INC) $(SRC) -o $(NAME)
	@echo "wheeltest created"

test: $(NAME)
	./$(NAME)

clean:
	@rm -f $(NAME)
	@echo "wheeltest cleaned"

re: clean $(NAME)
